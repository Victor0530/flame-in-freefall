"""Advisor retrieval, citation-audit and offline-fallback tests."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib import advisor  # noqa: E402


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Never call Gemini or write the real cache from the test suite."""
    monkeypatch.setattr(advisor, "_api_key", lambda: None)


def _passage(tag: str = "S1", doc_id: str = "psi-test") -> dict:
    return {
        "id": doc_id,
        "tag": tag,
        "text": (
            "BASS measured solid fuel spread and extinction across forced-flow conditions "
            "in microgravity, and the result differed from one-g testing."
        ),
        "source_label": "PSI record PSI-26 — BASS",
        "url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-26",
        "locator": "Approach",
        "kind": "psidata",
        "score": 0.9,
        "method": "tfidf",
        "scores": {"semantic": 0.0, "keyword": 0.9},
    }


def test_retrieve_returns_unique_tagged_passages() -> None:
    results = advisor.retrieve("How does ventilation change flame spread?", k=5)
    assert 1 <= len(results) <= 5
    assert [r["tag"] for r in results] == [f"S{i}" for i in range(1, len(results) + 1)]
    assert len({r["id"] for r in results}) == len(results)
    assert all(r["text"] for r in results)
    assert all(r["url"].startswith("https://") for r in results)
    assert [r["score"] for r in results] == sorted((r["score"] for r in results), reverse=True)


def test_retrieve_finds_named_experiment() -> None:
    results = advisor.retrieve("Which experiments used Saffire?", k=6)
    labels = " ".join(r["source_label"].lower() for r in results)
    assert "saffire" in labels
    assert results[0]["source_label"].lower().find("saffire") >= 0


def test_retrieve_handles_empty_question() -> None:
    assert advisor.retrieve("") == []
    assert advisor.retrieve("   ") == []


def test_semantic_ranking_maps_by_id_not_row_order(monkeypatch: pytest.MonkeyPatch) -> None:
    docs = [
        {"id": "a", "text": "alpha", "source_label": "A"},
        {"id": "b", "text": "beta", "source_label": "B"},
    ]
    vectors = {
        "ids": ["b", "a"],
        "matrix": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.float32),
    }
    monkeypatch.setattr(advisor, "_query_vector", lambda question: np.array([1.0, 0.0], dtype=np.float32))
    ranked = advisor._semantic_rank("query", {"docs": docs}, vectors)
    assert ranked is not None
    assert ranked[0][0]["id"] == "a"
    assert ranked[1][0]["id"] == "b"


def test_parse_citations_accepts_retrieved_tags_only() -> None:
    passages = [_passage("S1"), _passage("S2", "psi-two")]
    audit = advisor.parse_citations("Spread changed with flow [S1]. This is unsupported [S9].", passages)
    assert audit["cited"] == ["S1"]
    assert audit["unknown"] == ["S9"]
    assert audit["status"] == "unsupported"

    clean = advisor.parse_citations("Only this one [S2].", passages)
    assert clean["cited"] == ["S2"]
    assert clean["status"] == "ok"

    missing = advisor.parse_citations("No tag here.", passages)
    assert missing["status"] == "missing"


def test_reviewed_answer_bypasses_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args, **kwargs):
        raise AssertionError("retrieval should not run for a reviewed question")

    monkeypatch.setattr(advisor, "retrieve", fail)
    result = advisor.ask("What do we know about smoke detection in microgravity?")
    assert result["mode"] == "reviewed"
    assert result["citations"]["status"] == "reviewed"
    assert result["sources"]


def test_offline_answer_cites_and_caches(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(advisor, "retrieve", lambda question, k=6: [_passage()])
    monkeypatch.setattr(advisor, "CACHE_PATH", tmp_path / "answers.json")

    first = advisor.ask("What does BASS say about flow?", allow_generation=False)
    assert first["mode"] == "offline"
    assert first["citations"]["status"] == "ok"
    assert first["sources"][0]["tag"] == "S1"
    assert first["retrieved"][0]["id"] == "psi-test"

    second = advisor.ask("What does BASS say about flow?", allow_generation=False)
    assert second["mode"] == "cached"
    assert second["cached"] is True


def test_empty_question_has_empty_state() -> None:
    result = advisor.ask("   ")
    assert result["mode"] == "empty"
    assert result["sources"] == []


def test_no_match_has_empty_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(advisor, "retrieve", lambda question, k=6: [])
    result = advisor.ask("something outside the corpus")
    assert result["mode"] == "empty"
    assert result["citations"]["status"] == "empty"
