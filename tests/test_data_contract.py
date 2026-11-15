"""Data-contract tests beyond the smoke suite.

These are the checks that catch a bad rebuild before it reaches the app: encoding
damage, orphan condition rows, corpus/embedding drift, and broken FAQ citations.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.data import (  # noqa: E402
    badge,
    filter_records,
    load_conditions,
    load_faq,
    load_investigations,
    year_range,
)

DATA = ROOT / "data"
CORPUS = DATA / "corpus"


@pytest.fixture(scope="module")
def investigations() -> pd.DataFrame:
    return load_investigations()


@pytest.fixture(scope="module")
def conditions() -> pd.DataFrame:
    return load_conditions()


def test_no_replacement_characters() -> None:
    for path in [
        DATA / "investigations.csv",
        DATA / "test_conditions.csv",
        DATA / "faq.json",
        CORPUS / "chunks.jsonl",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "\ufffd" not in text, f"{path.name} contains a replacement character"


def test_phases_and_gravity_are_valid(investigations: pd.DataFrame) -> None:
    assert set(investigations["fire_safety_phase"]) <= {"prevention", "detection", "suppression"}
    assert set(investigations["gravity"]) <= {"microgravity", "1g"}


def test_sort_puts_flight_evidence_first(investigations: pd.DataFrame) -> None:
    assert investigations.iloc[0]["gravity"] == "microgravity"
    assert investigations.iloc[-1]["gravity"] == "1g"


def test_numeric_conditions_are_in_range(conditions: pd.DataFrame) -> None:
    o2 = pd.to_numeric(conditions["o2_pct"], errors="coerce").dropna()
    pressure = pd.to_numeric(conditions["pressure_kpa"], errors="coerce").dropna()
    flow = pd.to_numeric(conditions["flow_cm_s"], errors="coerce").dropna()
    assert o2.between(0, 100).all()
    assert (pressure > 0).all()
    assert (flow >= 0).all()


def test_faq_citations_are_sequential_and_complete() -> None:
    faq = load_faq()
    assert len(faq) == 6
    for item in faq:
        tags = [src["tag"] for src in item["sources"]]
        assert tags == [f"S{i}" for i in range(1, len(tags) + 1)]
        assert all(src["url"].startswith("https://") for src in item["sources"])
        assert all(src["locator"] for src in item["sources"])


def test_corpus_and_embedding_rows_are_aligned() -> None:
    docs = [
        json.loads(line)
        for line in (CORPUS / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ids = [doc["id"] for doc in docs]
    assert len(ids) == len(set(ids))
    loaded = np.load(CORPUS / "embeddings.npz", allow_pickle=False)
    vector_ids = [str(i) for i in loaded["ids"]]
    matrix = loaded["matrix"]
    assert len(vector_ids) == len(docs)
    assert set(vector_ids) == set(ids)
    assert matrix.shape[0] == len(docs)
    assert np.allclose(np.linalg.norm(matrix, axis=1), 1.0, atol=1e-3)


def test_cached_query_vectors_match_faq_hash() -> None:
    vectors = json.loads((CORPUS / "query_vectors.json").read_text(encoding="utf-8"))
    for item in load_faq():
        key = hashlib.sha1(item["question"].lower().strip().encode()).hexdigest()
        assert key in vectors


def test_filter_records_combines_filters(investigations: pd.DataFrame) -> None:
    soot = filter_records(investigations, query="soot", flight_only=True)
    assert len(soot) > 0
    assert (soot["gravity"] == "microgravity").all()
    assert soot.apply(
        lambda row: "soot" in " ".join(str(row[c]) for c in ["key_finding", "safety_implication", "objective", "materials", "name", "short_name", "measured_variables"]).lower(),
        axis=1,
    ).all()

    ground = filter_records(investigations, flight_only=False)
    assert len(ground) == len(investigations)

    prevention = filter_records(investigations, pillar="Prevention", flight_only=True)
    assert set(prevention["fire_safety_phase"]) == {"prevention"}

    empty = filter_records(investigations, query="no-such-term-anywhere")
    assert empty.empty


def test_badge_escapes_user_text() -> None:
    rendered = badge("<script>alert(1)</script>", "#ff0000")
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_year_range_formats_published_and_missing_years() -> None:
    assert year_range({"year_start": 2010, "year_end": 2012}) == "2010–2012"
    assert year_range({"year_start": 2010, "year_end": None}) == "2010"
    assert year_range({"year_start": None, "year_end": None}) == "dates not published"
