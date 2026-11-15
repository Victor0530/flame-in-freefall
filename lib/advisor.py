"""Retrieval-augmented evidence advisor.

Design rules:
- Retrieval combines local TF-IDF with optional Gemini embeddings. Either path
  works alone, so the app still answers with no network and no API key.
- Generation is optional. If Gemini is unavailable, the answer is extractive and
  cites the same passages.
- Every answer carries the passages it used and an audit of the citations in the
  generated text. Nothing is cited that was not retrieved.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data" / "corpus" / "chunks.jsonl"
VECTORS_PATH = ROOT / "data" / "corpus" / "embeddings.npz"
QUERY_VECTORS_PATH = ROOT / "data" / "corpus" / "query_vectors.json"
CACHE_PATH = ROOT / "data" / "cache" / "answers.json"

MODEL = "gemini-3.5-flash-lite"
EMBED_MODEL = "gemini-embedding-001"

MAX_QUESTION_CHARS = 500
CANDIDATES = 80
SEMANTIC_WEIGHT = 0.65
KEYWORD_WEIGHT = 0.35
MIN_RELATIVE_SCORE = 0.55
DEFAULT_K = 6

CITATION_RE = re.compile(r"\[S(\d+)\]")

SYSTEM_PROMPT = """You are a fire-safety evidence assistant for spacecraft habitats.
Answer ONLY from the numbered passages provided. Rules:
1. Cite every factual claim with its passage tag, like [S2].
2. Do not add qualifiers the passages do not contain. For example, do not describe an
   experiment as using "higher oxygen concentrations" unless a passage says so.
3. Ignore passages that do not address the question. Never merge unrelated studies into
   one sentence.
4. If the passages only partly answer the question, answer that part and name what is missing.
5. Distinguish microgravity flight evidence from ground or modelling evidence.
6. Never say a material, configuration, or atmosphere is "safe". Describe evidence strength.
7. Be concise: at most 120 words, plain prose, no headings.
8. If the passages do not answer the question, say so plainly and cite nothing."""

PROMPT_VERSION = "v3"

STOP = set(
    "the a an of and or in on for to is are was were what which how why with at as by from that this "
    "it its be been do does did can could should would we our you your about into than then there".split()
)

# Acronyms that users type as names. Exact matches should not lose to a semantically
# similar passage about a different experiment.
ACRONYMS = ("saffire", "bass", "acme", "flex", "same", "cfi", "slice", "spice", "daft")


@st.cache_resource(show_spinner=False)
def load_index() -> dict:
    """Load passages and fit the local TF-IDF index once per server process."""
    if not CORPUS_PATH.exists():
        return {"docs": [], "vectorizer": None, "matrix": None}

    docs: list[dict] = []
    for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            doc = json.loads(line)
        except json.JSONDecodeError:
            continue
        if doc.get("id") and doc.get("text"):
            docs.append(doc)

    if not docs:
        return {"docs": [], "vectorizer": None, "matrix": None}

    vectorizer = TfidfVectorizer(
        stop_words="english", ngram_range=(1, 2), sublinear_tf=True, min_df=1, max_features=60000
    )
    matrix = vectorizer.fit_transform([d["text"] for d in docs])
    return {"docs": docs, "vectorizer": vectorizer, "matrix": matrix}


@st.cache_resource(show_spinner=False)
def load_vectors() -> dict | None:
    """Load precomputed embeddings, validating that ids and rows agree."""
    if not VECTORS_PATH.exists():
        return None
    try:
        data = np.load(VECTORS_PATH, allow_pickle=False)
        ids = [str(i) for i in data["ids"]]
        matrix = np.asarray(data["matrix"], dtype=np.float32)
    except Exception:
        return None
    if matrix.ndim != 2 or len(ids) != matrix.shape[0] or not np.isfinite(matrix).all():
        return None
    return {"ids": ids, "matrix": matrix}


@lru_cache(maxsize=1)
def corpus_version() -> str:
    """Short fingerprint of the corpus so stale cached answers are not reused."""
    if not CORPUS_PATH.exists():
        return "missing"
    digest = hashlib.sha1(CORPUS_PATH.read_bytes()).hexdigest()
    return digest[:12]


def _hash(text: str) -> str:
    return hashlib.sha1(text.lower().strip().encode()).hexdigest()


def api_key_available() -> bool:
    return bool(_api_key())


def _api_key() -> str | None:
    try:
        key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        key = None
    return key or os.getenv("GEMINI_API_KEY")


def _query_vector(question: str) -> np.ndarray | None:
    """Cached vector for known questions, otherwise one live embedding call."""
    cached: dict = {}
    if QUERY_VECTORS_PATH.exists():
        try:
            cached = json.loads(QUERY_VECTORS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cached = {}
    key = _hash(question)
    if key in cached:
        try:
            vec = np.asarray(cached[key], dtype=np.float32)
        except (TypeError, ValueError):
            vec = None
        if vec is not None and vec.ndim == 1 and np.isfinite(vec).all():
            return vec

    api = _api_key()
    if not api:
        return None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api)
        resp = client.models.embed_content(
            model=EMBED_MODEL,
            contents=[question],
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY", output_dimensionality=768),
        )
        vec = np.asarray(resp.embeddings[0].values, dtype=np.float32)
        vec /= np.linalg.norm(vec) + 1e-9
        cached[key] = vec.tolist()
        tmp = QUERY_VECTORS_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(cached), encoding="utf-8")
        os.replace(tmp, QUERY_VECTORS_PATH)
        return vec
    except Exception:
        return None


def _keyword_rank(question: str, index: dict) -> list[tuple[dict, float]]:
    """TF-IDF ranking over the local corpus."""
    vectorizer = index.get("vectorizer")
    matrix = index.get("matrix")
    if vectorizer is None or matrix is None:
        return []
    query = vectorizer.transform([question])
    sims = cosine_similarity(query, matrix).ravel()
    order = np.argsort(sims)[::-1]
    docs = index["docs"]
    return [
        (docs[int(i)], float(sims[int(i)]))
        for i in order[:CANDIDATES]
        if sims[int(i)] > 0
    ]


def _semantic_rank(
    question: str, index: dict, vectors: dict | None
) -> list[tuple[dict, float]] | None:
    """Vector ranking mapped by document id, never by row position alone."""
    if vectors is None:
        return None
    query_vec = _query_vector(question)
    if query_vec is None:
        return None
    matrix = vectors["matrix"]
    if matrix.shape[1] != query_vec.shape[0]:
        return None

    scores = matrix @ query_vec
    order = np.argsort(scores)[::-1]
    docs_by_id = {doc["id"]: doc for doc in index["docs"]}
    out: list[tuple[dict, float]] = []
    for i in order[:CANDIDATES]:
        doc = docs_by_id.get(vectors["ids"][int(i)])
        if doc is not None:
            out.append((doc, float(scores[int(i)])))
    return out


def _normalise(pairs: list[tuple[dict, float]]) -> dict[str, float]:
    if not pairs:
        return {}
    values = [score for _, score in pairs]
    low, high = min(values), max(values)
    if high - low < 1e-9:
        return {doc["id"]: 1.0 for doc, _ in pairs}
    return {doc["id"]: (score - low) / (high - low) for doc, score in pairs}


def _exact_term_boost(question: str, doc: dict) -> float:
    """Prefer exact names and acronyms over a merely similar passage."""
    haystack = f"{doc.get('source_label', '')} {doc.get('text', '')}".lower()
    terms = [w for w in re.findall(r"[a-z]{4,}", question.lower()) if w not in STOP]
    hits = sum(1 for term in terms if term in haystack)
    boost = 0.02 * hits
    for acronym in ACRONYMS:
        if acronym in question.lower() and acronym in haystack:
            boost += 0.08
    if re.search(r"\b(which|what)\s+experiments?\b", question.lower()) and doc.get("kind") in {
        "psidata",
        "condition",
    }:
        boost += 0.05
    return boost


def _fuse(
    question: str,
    keyword: list[tuple[dict, float]],
    semantic: list[tuple[dict, float]] | None,
) -> list[tuple[dict, float, dict]]:
    keyword_norm = _normalise(keyword)
    semantic_norm = _normalise(semantic or [])
    keyword_scores = {doc["id"]: score for doc, score in keyword}
    semantic_scores = {doc["id"]: score for doc, score in semantic or []}
    docs = {doc["id"]: doc for doc, _ in keyword}
    if semantic:
        docs.update({doc["id"]: doc for doc, _ in semantic})

    fused = []
    for doc_id, doc in docs.items():
        sem = semantic_norm.get(doc_id, 0.0)
        kw = keyword_norm.get(doc_id, 0.0)
        if semantic is None:
            score = keyword_norm.get(doc_id, 0.0)
        else:
            score = SEMANTIC_WEIGHT * sem + KEYWORD_WEIGHT * kw
        score += _exact_term_boost(question, doc)
        fused.append(
            (
                doc,
                score,
                {
                    "semantic": round(semantic_scores.get(doc_id, 0.0), 4),
                    "keyword": round(keyword_scores.get(doc_id, 0.0), 4),
                },
            )
        )
    return sorted(fused, key=lambda item: -item[1])


def _retrieve(question: str, k: int = DEFAULT_K) -> list[dict]:
    question = (question or "").strip()
    if not question:
        return []

    index = load_index()
    if not index["docs"]:
        return []

    keyword = _keyword_rank(question, index)
    semantic = _semantic_rank(question, index, load_vectors())
    fused = _fuse(question, keyword, semantic)
    if not fused:
        return []

    # Keep only results close to the best match. A weak tail is worse than a
    # short list: it invites citations that do not support the answer.
    top = fused[0][1]
    kept = [item for item in fused if item[1] >= MIN_RELATIVE_SCORE * top][:k]
    if not kept:
        kept = fused[:1]

    method = "hybrid" if semantic else "tfidf"
    out = []
    for rank, (doc, score, parts) in enumerate(kept, start=1):
        item = dict(doc)
        item["tag"] = f"S{rank}"
        item["score"] = round(float(score), 3)
        item["method"] = method
        item["scores"] = parts
        out.append(item)
    return out


def retrieve(question: str, k: int = DEFAULT_K) -> list[dict]:
    """Public retrieval entry point used by the UI and tests."""
    return _retrieve(question, k=k)


def parse_citations(answer: str, passages: list[dict]) -> dict:
    """Report which retrieved tags the answer cites, and any invented tags."""
    available = {p["tag"] for p in passages}
    cited: list[str] = []
    unknown: list[str] = []
    for match in CITATION_RE.finditer(answer or ""):
        tag = f"S{match.group(1)}"
        if tag in available:
            if tag not in cited:
                cited.append(tag)
        elif tag not in unknown:
            unknown.append(tag)
    status = "ok" if cited and not unknown else "missing" if not cited else "unsupported"
    return {"cited": cited, "unknown": unknown, "status": status}


def _cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(data: dict) -> None:
    """Write atomically so an interrupted run cannot corrupt the cache."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, CACHE_PATH)


def _generate(question: str, passages: list[dict]) -> str | None:
    key = _api_key()
    if not key:
        return None
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None

    context = "\n\n".join(f"[{p['tag']}] {p['text']}" for p in passages)
    contents = f"Passages:\n{context}\n\nQuestion: {question}"
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
                max_output_tokens=420,
            ),
        )
        text = (response.text or "").strip()
        return text or None
    except Exception:
        return None


def _extractive(question: str, passages: list[dict]) -> str:
    terms = {w for w in re.findall(r"[a-z0-9]+", question.lower()) if w not in STOP and len(w) > 3}
    scored: list[tuple[int, str, str]] = []
    for p in passages[:5]:
        for sentence in re.split(r"(?<=[.!?])\s+", p["text"]):
            sentence = sentence.strip()
            if len(sentence) < 60:
                continue
            hits = len(terms & set(re.findall(r"[a-z0-9]+", sentence.lower())))
            if hits:
                scored.append((hits, sentence, p["tag"]))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        return (
            "The retrieved NASA passages do not directly address this question. "
            "Try asking about a specific experiment, atmosphere, or fire-safety phase."
        )
    bullets = " ".join(f"{sentence} [{tag}]" for _, sentence, tag in scored[:4])
    return (
        "No language model is available, so this answer quotes the retrieved sources "
        f"directly. {bullets}"
    )


def _normalise_question(text: str) -> str:
    return " ".join(text.lower().split()).rstrip("?.!")


@st.cache_data(show_spinner=False)
def _faq() -> list[dict]:
    path = ROOT / "data" / "faq.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("items", [])
    except (json.JSONDecodeError, OSError):
        return []


def _reviewed_answer(question: str) -> dict | None:
    """Serve the human-reviewed answer set before any model call."""
    target = _normalise_question(question)
    for item in _faq():
        if _normalise_question(item["question"]) == target:
            sources = [{**src, "kind": "reviewed", "score": 1.0} for src in item["sources"]]
            return {
                "answer": item["answer"],
                "sources": sources,
                "retrieved": [],
                "citations": {"cited": [s["tag"] for s in sources], "unknown": [], "status": "reviewed"},
                "mode": "reviewed",
                "cached": False,
            }
    return None


def _passages_from_sources(sources: list[dict]) -> list[dict]:
    return [
        {
            "tag": s.get("tag", ""),
            "source_label": s.get("label", ""),
            "label": s.get("label", ""),
            "url": s.get("url", ""),
            "locator": s.get("locator", ""),
            "kind": s.get("kind", "reviewed"),
            "score": s.get("score", 1.0),
            "text": "",
        }
        for s in sources
    ]


def ask(question: str, k: int = DEFAULT_K, allow_generation: bool = True) -> dict:
    """Answer a question, degrading to extractive quotations when needed."""
    question = (question or "").strip()[:MAX_QUESTION_CHARS]
    if not question:
        return {
            "answer": "Enter a question about a NASA combustion experiment or habitat atmosphere.",
            "sources": [],
            "retrieved": [],
            "citations": {"cited": [], "unknown": [], "status": "empty"},
            "mode": "empty",
            "cached": False,
        }

    reviewed = _reviewed_answer(question)
    if reviewed:
        return reviewed

    passages = retrieve(question, k=k)
    if not passages:
        return {
            "answer": (
                "Nothing in the 222-passage corpus matched that question. Try naming an "
                "experiment (Saffire, BASS, FLEX), a material, or an atmosphere."
            ),
            "sources": [],
            "retrieved": [],
            "citations": {"cited": [], "unknown": [], "status": "empty"},
            "mode": "empty",
            "cached": False,
        }

    key = hashlib.sha1(
        json.dumps(
            [
                MODEL,
                PROMPT_VERSION,
                corpus_version(),
                question.lower(),
                [p["id"] for p in passages],
            ]
        ).encode()
    ).hexdigest()

    cache = _cache()
    entry = cache.get(key)
    if entry and (allow_generation or entry.get("mode") == "offline"):
        answer = entry.get("answer", "")
        audit = parse_citations(answer, passages)
        sources = entry.get("sources") or []
        if not sources:
            sources = _sources_for(passages, audit)
        return {
            "answer": answer,
            "sources": sources,
            "retrieved": passages,
            "citations": audit,
            "mode": "cached",
            "cached": True,
        }

    text = _generate(question, passages) if allow_generation else None
    mode = "gemini" if text else "offline"
    if not text:
        text = _extractive(question, passages)

    audit = parse_citations(text, passages)
    sources = _sources_for(passages, audit)
    cache[key] = {"question": question, "answer": text, "sources": sources, "mode": mode}
    _save_cache(cache)
    return {
        "answer": text,
        "sources": sources,
        "retrieved": passages,
        "citations": audit,
        "mode": mode,
        "cached": False,
    }


def _sources_for(passages: list[dict], audit: dict) -> list[dict]:
    """Prefer only cited passages; fall back to all retrieved if none were cited."""
    cited = set(audit.get("cited", []))
    selected = [p for p in passages if p["tag"] in cited] if cited else passages
    return [
        {
            "tag": p["tag"],
            "label": p["source_label"],
            "url": p["url"],
            "locator": p["locator"],
            "kind": p["kind"],
            "score": round(p["score"], 3),
        }
        for p in selected
    ]


def sources_to_passages(sources: list[dict]) -> list[dict]:
    """Rebuild display passages for a reviewed answer (no retrieval text)."""
    return _passages_from_sources(sources)
