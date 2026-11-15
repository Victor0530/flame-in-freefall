"""Precompute embedding vectors so semantic retrieval works without a live query call.

Docs: data/corpus/chunks.jsonl -> data/corpus/embeddings.npz (ids + matrix)
FAQ query vectors: data/corpus/query_vectors.json (text hash -> vector)

The runtime hash normalises with .lower().strip(); this script uses the same
normalisation so cached query vectors are actually found.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import tomllib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "corpus"
MODEL = "gemini-embedding-001"
DIMS = 768

FAQ = [
    "Which experiments tested flammability at high oxygen concentration?",
    "What do we know about smoke detection in microgravity?",
    "How is a microgravity fire suppressed?",
    "What should a Moon habitat test first?",
    "How does the 34% oxygen atmosphere compare with NASA-STD-6001 Test 1?",
    "Why is 1-g material screening not sufficient for spacecraft?",
]


def api_key() -> str:
    secrets = ROOT / ".streamlit" / "secrets.toml"
    key = os.getenv("GEMINI_API_KEY")
    if not key and secrets.exists():
        try:
            data = tomllib.loads(secrets.read_text(encoding="utf-8"))
            key = data.get("GEMINI_API_KEY")
        except (tomllib.TOMLDecodeError, OSError) as exc:
            raise SystemExit(f"could not read {secrets}: {exc}") from exc
    if not key:
        raise SystemExit(
            "No Gemini API key. Set GEMINI_API_KEY or add it to .streamlit/secrets.toml. "
            "The app still works without embeddings using local TF-IDF retrieval."
        )
    return key


def embed_all(client, texts: list[str], task_type: str) -> list[list[float]]:
    """Embed within the free-tier limit (~100 requests/minute, counted per text)."""
    from google.genai import types

    vectors: list[list[float]] = []
    batch = 16
    for start in range(0, len(texts), batch):
        chunk = texts[start : start + batch]
        for attempt in range(6):
            try:
                resp = client.models.embed_content(
                    model=MODEL,
                    contents=chunk,
                    config=types.EmbedContentConfig(
                        task_type=task_type, output_dimensionality=DIMS
                    ),
                )
                if len(resp.embeddings) != len(chunk):
                    raise RuntimeError(
                        f"expected {len(chunk)} embeddings, got {len(resp.embeddings)}"
                    )
                vectors.extend([e.values for e in resp.embeddings])
                break
            except Exception as exc:  # rate limit or transient failure
                if attempt == 5:
                    raise
                wait = 30 if "RESOURCE_EXHAUSTED" in str(exc) else 5
                print(f"  retry in {wait}s ({type(exc).__name__})")
                time.sleep(wait)
        time.sleep(6)
        print(f"embedded {min(start + batch, len(texts))}/{len(texts)}")
    return vectors


def main() -> None:
    from google import genai

    if not (CORPUS / "chunks.jsonl").exists():
        raise SystemExit("data/corpus/chunks.jsonl is missing; run scripts/build_corpus.py first")

    client = genai.Client(api_key=api_key())
    docs = [
        json.loads(line)
        for line in (CORPUS / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    texts = [d["text"] for d in docs]
    ids = [d["id"] for d in docs]
    if len(set(ids)) != len(ids):
        raise SystemExit("chunks.jsonl has duplicate ids; rebuild the corpus first")
    if not texts:
        raise SystemExit("chunks.jsonl is empty")

    vectors = embed_all(client, texts, "RETRIEVAL_DOCUMENT")
    if len(vectors) != len(texts):
        raise SystemExit(f"embedding count mismatch: {len(vectors)} != {len(texts)}")

    matrix = np.asarray(vectors, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[1] != DIMS or not np.isfinite(matrix).all():
        raise SystemExit(f"unexpected embedding matrix shape {matrix.shape}")
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-9

    path = CORPUS / "embeddings.npz"
    tmp = CORPUS / "embeddings.tmp"
    with tmp.open("wb") as fh:
        np.savez_compressed(fh, ids=np.array(ids), matrix=matrix)
    os.replace(tmp, path)
    print("wrote embeddings.npz", matrix.shape)

    qvecs = {}
    qvec_list = embed_all(client, FAQ, "RETRIEVAL_QUERY")
    for text, values in zip(FAQ, qvec_list):
        vec = np.asarray(values, dtype=np.float32)
        if vec.shape != (DIMS,):
            raise SystemExit(f"unexpected query vector shape {vec.shape}")
        vec /= np.linalg.norm(vec) + 1e-9
        qvecs[hashlib.sha1(text.lower().strip().encode()).hexdigest()] = vec.tolist()
    qpath = CORPUS / "query_vectors.json"
    qtmp = CORPUS / "query_vectors.tmp"
    qtmp.write_text(json.dumps(qvecs), encoding="utf-8")
    os.replace(qtmp, qpath)
    print("wrote query_vectors.json", len(qvecs))


if __name__ == "__main__":
    sys.exit(main())
