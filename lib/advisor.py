"""Retrieval-augmented evidence advisor.

Design rules:
- Retrieval is local TF-IDF, so the app works with no network and no API key.
- Generation is optional. If Gemini is unavailable, the answer is extractive and
  cites the same passages.
- Every answer carries the passages it used. Nothing is cited that was not retrieved.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data" / "corpus" / "chunks.jsonl"
CACHE_PATH = ROOT / "data" / "cache" / "answers.json"

MODEL = "gemini-3.5-flash-lite"
EMBED_MODEL = "gemini-embedding-001"

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
7. Be concise: at most 120 words, plain prose, no headings."""

PROMPT_VERSION = "v2"


@st.cache_resource(show_spinner=False)
def load_index() -> dict:
    docs = [json.loads(line) for line in CORPUS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    texts = [d["text"] for d in docs]
    vectorizer = TfidfVectorizer(
        stop_words="english", ngram_range=(1, 2), sublinear_tf=True, min_df=1, max_features=60000
    )
    matrix = vectorizer.fit_transform(texts)
    return {"docs": docs, "vectorizer": vectorizer, "matrix": matrix}


VECTORS_PATH = CORPUS_PATH.parent / "embeddings.npz"
QUERY_VECTORS_PATH = CORPUS_PATH.parent / "query_vectors.json"


@st.cache_resource(show_spinner=False)
def load_vectors() -> dict | None:
    if not VECTORS_PATH.exists():
        return None
    data = np.load(VECTORS_PATH, allow_pickle=False)
    return {"ids": [str(i) for i in data["ids"]], "matrix": data["matrix"]}


def _hash(text: str) -> str:
    return hashlib.sha1(text.lower().strip().encode()).hexdigest()


def _query_vector(question: str) -> np.ndarray | None:
    """Cached vector for known questions, otherwise one live embedding call."""
    cached: dict = {}
    if QUERY_VECTORS_PATH.exists():
        try:
            cached = json.loads(QUERY_VECTORS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cached = {}
    key = _hash(question)
    if key in cached:
        return np.asarray(cached[key], dtype=np.float32)

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
        QUERY_VECTORS_PATH.write_text(json.dumps(cached), encoding="utf-8")
        return vec
    except Exception:
        return None


def _keyword_boost(question: str, doc: dict) -> float:
    """Acronyms like SAFFIRE or BASS should not lose to a semantically similar passage."""
    haystack = f"{doc['source_label']} {doc['text']}".lower()
    terms = [w for w in re.findall(r"[a-z]{4,}", question.lower()) if w not in STOP]
    hits = sum(1 for t in terms if t in haystack)
    boost = 0.03 * hits
    if re.search(r"\b(which|what)\s+experiments?\b", question.lower()) and doc["kind"] in {
        "psidata",
        "condition",
    }:
        boost += 0.05
    return boost


def retrieve(question: str, k: int = 6) -> list[dict]:
    idx = load_index()
    vectors = load_vectors()
    query_vec = _query_vector(question) if vectors else None

    if vectors is not None and query_vec is not None:
        scores = vectors["matrix"] @ query_vec
        order = np.argsort(scores)[::-1]
        docs = idx["docs"]
        ranked = []
        for i in order:
            doc = docs[int(i)]
            ranked.append((float(scores[int(i)]) + _keyword_boost(question, doc), doc))
        ranked.sort(key=lambda x: -x[0])
        chosen = ranked[: k * 2]
        method = "semantic"
    else:
        query = idx["vectorizer"].transform([question])
        sims = cosine_similarity(query, idx["matrix"]).ravel()
        order = np.argsort(sims)[::-1]
        chosen = [(float(sims[int(i)]), idx["docs"][int(i)]) for i in order[: k * 2] if sims[int(i)] > 0]
        method = "tfidf"

    out = []
    kept = [c for c in chosen if c[0] > 0][:k]
    if kept and method == "semantic":
        top = kept[0][0]
        kept = [c for c in kept if c[0] >= 0.80 * top][:k]
    for rank, (score, doc) in enumerate(kept, start=1):
        item = dict(doc)
        item["tag"] = f"S{rank}"
        item["score"] = score
        item["method"] = method
        out.append(item)
    return out



def _cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def _save_cache(data: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _api_key() -> str | None:
    try:
        key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        key = None
    return key or os.getenv("GEMINI_API_KEY")


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


STOP = set(
    "the a an of and or in on for to is are was were what which how why with at as by from that this "
    "it its be been do does did can could should would we our you your about into than then there".split()
)


def _extractive(question: str, passages: list[dict]) -> str:
    terms = {w for w in re.findall(r"[a-z0-9]+", question.lower()) if w not in STOP and len(w) > 3}
    scored: list[tuple[int, str, str]] = []
    for p in passages[:4]:
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
    top = scored[:4]
    bullets = " ".join(f"{sentence} [{tag}]" for _, sentence, tag in top)
    return f"No language model available, so this answer quotes the retrieved sources directly. {bullets}"


def _normalise(text: str) -> str:
    return " ".join(text.lower().split()).rstrip("?.!")


@st.cache_data(show_spinner=False)
def _faq() -> list[dict]:
    path = ROOT / "data" / "faq.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("items", [])


def _reviewed_answer(question: str) -> dict | None:
    """Serve the human-reviewed answer set before any model call."""
    target = _normalise(question)
    for item in _faq():
        if _normalise(item["question"]) == target:
            return {
                "answer": item["answer"],
                "sources": [
                    {**src, "kind": "reviewed", "score": 1.0} for src in item["sources"]
                ],
                "mode": "reviewed",
                "cached": False,
            }
    return None


def ask(question: str, k: int = 6, allow_generation: bool = True) -> dict:
    question = question.strip()
    reviewed = _reviewed_answer(question)
    if reviewed:
        return reviewed
    passages = retrieve(question, k=k)
    if not passages:
        return {
            "answer": "Nothing in the corpus matched that question.",
            "sources": [],
            "mode": "empty",
            "cached": False,
        }

    key = hashlib.sha1(
        json.dumps([MODEL, PROMPT_VERSION, question.lower(), [p["id"] for p in passages]]).encode()
    ).hexdigest()
    cache = _cache()
    if key in cache:
        entry = cache[key]
        return {
            "answer": entry["answer"],
            "sources": entry["sources"],
            "mode": entry.get("mode", "cached"),
            "cached": True,
        }

    text = _generate(question, passages) if allow_generation else None
    mode = "gemini" if text else "offline"
    if not text:
        text = _extractive(question, passages)

    sources = [
        {
            "tag": p["tag"],
            "label": p["source_label"],
            "url": p["url"],
            "locator": p["locator"],
            "kind": p["kind"],
            "score": round(p["score"], 3),
        }
        for p in passages
    ]
    cache[key] = {"question": question, "answer": text, "sources": sources, "mode": mode}
    _save_cache(cache)
    return {"answer": text, "sources": sources, "mode": mode, "cached": False}
