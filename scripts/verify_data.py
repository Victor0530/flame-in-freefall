"""Verify the data contract before the app is deployed.

Run: python scripts/verify_data.py

Checks the curated CSVs, the FAQ, the retrieval corpus, the embedding matrix and
the query-vector cache. Exits non-zero when anything is inconsistent, so it can
gate a rebuild or a deployment.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CORPUS = DATA / "corpus"

NUMERIC_TYPES = {"specific", "range"}
PHASES = {"prevention", "detection", "suppression"}
GRAVITY = {"microgravity", "1g"}
REQUIRED_INVESTIGATION_COLUMNS = {
    "id",
    "name",
    "short_name",
    "program",
    "fire_safety_phase",
    "gravity",
    "objective",
    "materials",
    "measured_variables",
    "key_finding",
    "safety_implication",
    "limitations",
    "psi_id",
    "psi_url",
}
REQUIRED_CONDITION_COLUMNS = {
    "investigation_id",
    "short_name",
    "point_label",
    "point_type",
    "gravity",
    "o2_pct",
    "pressure_kpa",
    "flow_cm_s",
    "source_url",
    "source_locator",
    "source_quote",
}
REQUIRED_DOC_FIELDS = {"id", "text", "source_label", "url", "locator", "kind"}


class Checks:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passes = 0

    def check(self, condition: bool, message: str, detail: str = "") -> None:
        if condition:
            self.passes += 1
        else:
            self.failures.append(f"{message}{(': ' + detail) if detail else ''}")

    def report(self) -> int:
        print(f"\n{self.passes} checks passed, {len(self.failures)} failed")
        for failure in self.failures:
            print(f"  FAIL  {failure}")
        return 0 if not self.failures else 1


def _url_ok(value: str) -> bool:
    return str(value).startswith(("https://", "http://"))


def _no_replacement(value: str) -> bool:
    return "\ufffd" not in str(value)


def check_investigations(c: Checks) -> pd.DataFrame:
    path = DATA / "investigations.csv"
    c.check(path.exists(), "investigations.csv exists")
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = REQUIRED_INVESTIGATION_COLUMNS - set(df.columns)
    c.check(not missing, "investigations.csv has required columns", ", ".join(sorted(missing)))
    c.check(len(df) == 24, "24 investigations are present", str(len(df)))
    c.check(df["id"].is_unique, "investigation ids are unique")
    c.check(df["psi_id"].is_unique, "PSI accessions are unique")
    c.check(set(df["fire_safety_phase"]).issubset(PHASES), "fire-safety phases are valid")
    c.check(set(df["gravity"]).issubset(GRAVITY), "gravity labels are valid")

    for column in ["name", "short_name", "key_finding", "safety_implication"]:
        c.check(
            df[column].str.strip().str.len().min() > 0,
            f"investigations.{column} is never blank",
        )
    c.check(
        df["psi_url"].map(_url_ok).all(),
        "every PSI record has an http(s) URL",
    )
    years = pd.to_numeric(df["year_start"], errors="coerce").dropna()
    c.check(years.between(1950, 2030).all(), "start years are plausible")
    for column in df.columns:
        if df[column].dtype == object:
            c.check(
                df[column].map(_no_replacement).all(),
                f"investigations.{column} has no replacement characters",
            )
    return df


def check_conditions(c: Checks, investigations: pd.DataFrame) -> pd.DataFrame:
    path = DATA / "test_conditions.csv"
    c.check(path.exists(), "test_conditions.csv exists")
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = REQUIRED_CONDITION_COLUMNS - set(df.columns)
    c.check(not missing, "test_conditions.csv has required columns", ", ".join(sorted(missing)))
    c.check(len(df) > 0, "condition rows exist")
    c.check(
        set(df["investigation_id"]).issubset(set(investigations["psi_id"])),
        "condition rows point at real investigations",
    )
    c.check(
        set(df["point_type"]).issubset({"specific", "range", "qualitative", "ground"}),
        "condition types are valid",
    )
    c.check(
        not df.duplicated(["investigation_id", "point_label"]).any(),
        "condition labels are unique per investigation",
    )

    numeric = df[df["point_type"].isin(NUMERIC_TYPES)].copy()
    for column in ("o2_pct", "pressure_kpa", "flow_cm_s"):
        values = pd.to_numeric(numeric[column].replace("", pd.NA), errors="coerce")
        documented = numeric[values.notna()]
        c.check(
            documented["source_quote"].str.len().min() > 20,
            f"numeric {column} rows carry a source quote",
        )
        c.check(
            documented["source_locator"].str.len().min() > 3,
            f"numeric {column} rows carry a locator",
        )
        c.check(
            documented["source_url"].map(_url_ok).all(),
            f"numeric {column} rows carry an http(s) source URL",
        )

    o2 = pd.to_numeric(df["o2_pct"].replace("", pd.NA), errors="coerce").dropna()
    pressure = pd.to_numeric(df["pressure_kpa"].replace("", pd.NA), errors="coerce").dropna()
    flow = pd.to_numeric(df["flow_cm_s"].replace("", pd.NA), errors="coerce").dropna()
    c.check(o2.between(0, 100).all(), "O2 fractions are between 0 and 100")
    c.check((pressure > 0).all(), "pressures are positive")
    c.check((flow >= 0).all(), "flow speeds are non-negative")
    return df


def check_faq(c: Checks) -> list[dict]:
    path = DATA / "faq.json"
    c.check(path.exists(), "faq.json exists")
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    c.check(len(items) == 6, "six reviewed answers exist", str(len(items)))
    questions = [item.get("question", "") for item in items]
    c.check(len(set(questions)) == len(questions), "reviewed questions are unique")
    for item in items:
        sources = item.get("sources", [])
        c.check(len(item.get("answer", "")) > 80, f"reviewed answer is substantive: {item.get('question', '')[:50]}")
        c.check(len(sources) >= 1, f"reviewed answer has sources: {item.get('question', '')[:50]}")
        tags = [src.get("tag", "") for src in sources]
        c.check(
            tags == [f"S{i}" for i in range(1, len(tags) + 1)],
            f"reviewed source tags are sequential: {item.get('question', '')[:50]}",
        )
        c.check(
            all(_url_ok(src.get("url", "")) for src in sources),
            f"reviewed sources have http(s) URLs: {item.get('question', '')[:50]}",
        )
        c.check(
            all(src.get("locator") for src in sources),
            f"reviewed sources have locators: {item.get('question', '')[:50]}",
        )
    return items


def check_corpus(c: Checks) -> list[dict]:
    path = CORPUS / "chunks.jsonl"
    c.check(path.exists(), "chunks.jsonl exists")
    docs = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            doc = json.loads(line)
        except json.JSONDecodeError as exc:
            c.check(False, f"chunks.jsonl line {number} is valid JSON", str(exc))
            continue
        docs.append(doc)

    c.check(len(docs) > 100, "corpus has more than 100 passages", str(len(docs)))
    c.check(len({doc.get("id") for doc in docs}) == len(docs), "passage ids are unique")
    c.check(
        all(REQUIRED_DOC_FIELDS.issubset(doc) for doc in docs),
        "every passage has id, text, label, url, locator and kind",
    )
    c.check(
        all(_url_ok(doc.get("url", "")) for doc in docs),
        "every passage has an http(s) source URL",
    )
    c.check(all(doc.get("text", "").strip() for doc in docs), "no passage has empty text")
    c.check(
        all(_no_replacement(doc.get("text", "")) for doc in docs),
        "corpus text has no replacement characters",
    )
    kinds = {doc.get("kind") for doc in docs}
    c.check(
        {"psidata", "condition", "ntrs", "standard"}.issubset(kinds),
        "corpus covers PSI, conditions, NTRS and standards",
        ", ".join(sorted(str(k) for k in kinds)),
    )
    return docs


def check_embeddings(c: Checks, docs: list[dict]) -> None:
    path = CORPUS / "embeddings.npz"
    c.check(path.exists(), "embeddings.npz exists")
    if not path.exists():
        return
    loaded = np.load(path, allow_pickle=False)
    ids = [str(i) for i in loaded["ids"]]
    matrix = np.asarray(loaded["matrix"], dtype=np.float32)
    c.check(matrix.ndim == 2, "embedding matrix is two-dimensional")
    c.check(len(ids) == len(docs), "one embedding per passage", f"{len(ids)} != {len(docs)}")
    c.check(len(set(ids)) == len(ids), "embedding ids are unique")
    c.check(set(ids) == {doc["id"] for doc in docs}, "embedding ids match the corpus")
    c.check(matrix.shape[0] == len(ids), "embedding rows match ids", f"{matrix.shape[0]} != {len(ids)}")
    c.check(np.isfinite(matrix).all(), "embedding values are finite")
    norms = np.linalg.norm(matrix, axis=1)
    c.check(
        bool(np.allclose(norms, 1.0, atol=1e-3)),
        "embedding rows are unit-normalised",
        f"min={norms.min():.3f} max={norms.max():.3f}",
    )
    c.check(matrix.shape[1] in {768, 1536, 3072}, "embedding dimension is a known Gemini size", str(matrix.shape[1]))


def check_query_vectors(c: Checks, faq: list[dict]) -> None:
    path = CORPUS / "query_vectors.json"
    c.check(path.exists(), "query_vectors.json exists")
    if not path.exists():
        return
    vectors = json.loads(path.read_text(encoding="utf-8"))
    for item in faq:
        question = item.get("question", "")
        key = hashlib.sha1(question.lower().strip().encode()).hexdigest()
        c.check(key in vectors, f"cached query vector exists: {question[:50]}")
        if key in vectors:
            vec = np.asarray(vectors[key], dtype=np.float32)
            c.check(vec.ndim == 1, f"query vector is one-dimensional: {question[:50]}")
            c.check(np.isfinite(vec).all(), f"query vector is finite: {question[:50]}")


def main() -> int:
    checks = Checks()
    investigations = check_investigations(checks)
    check_conditions(checks, investigations)
    faq = check_faq(checks)
    docs = check_corpus(checks)
    check_embeddings(checks, docs)
    check_query_vectors(checks, faq)
    return checks.report()


if __name__ == "__main__":
    sys.exit(main())
