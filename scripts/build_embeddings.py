"""Precompute embedding vectors so semantic retrieval works without a live query call.

Docs: data/corpus/chunks.jsonl -> data/corpus/embeddings.npz (ids + matrix)
FAQ query vectors: data/corpus/query_vectors.json (text hash -> vector)
"""

from __future__ import annotations

import hashlib
import json
import pathlib
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
    data = tomllib.loads(secrets.read_text(encoding="utf-8"))
    return data["GEMINI_API_KEY"]


def embed_all(client, texts: list[str], task_type: str) -> list[list[float]]:
    """Embed within the free-tier limit (~100 requests/minute, counted per text)."""
    import time

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

    client = genai.Client(api_key=api_key())
    docs = [json.loads(line) for line in (CORPUS / "chunks.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    texts = [d["text"] for d in docs]
    ids = [d["id"] for d in docs]

    vectors = embed_all(client, texts, "RETRIEVAL_DOCUMENT")

    matrix = np.asarray(vectors, dtype=np.float32)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-9
    np.savez_compressed(CORPUS / "embeddings.npz", ids=np.array(ids), matrix=matrix)
    print("wrote embeddings.npz", matrix.shape)

    qvecs = {}
    qvec_list = embed_all(client, FAQ, "RETRIEVAL_QUERY")
    for text, values in zip(FAQ, qvec_list):
        vec = np.asarray(values, dtype=np.float32)
        vec /= np.linalg.norm(vec) + 1e-9
        qvecs[hashlib.sha1(text.lower().encode()).hexdigest()] = vec.tolist()
    (CORPUS / "query_vectors.json").write_text(json.dumps(qvecs), encoding="utf-8")
    print("wrote query_vectors.json", len(qvecs))


if __name__ == "__main__":
    main()
