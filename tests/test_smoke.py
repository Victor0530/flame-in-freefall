"""Smoke tests for the curated data contract and the ranking.

These tests are deliberately about *evidence integrity*: every numeric condition must
carry a quoted source, blanks must stay blank, and the ranking must never score a
dimension it has no data for.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.data import CORE_IDS, load_conditions, load_faq, load_investigations  # noqa: E402
from lib.scoring import WEIGHTS, rank_all, score_investigation  # noqa: E402

NUMERIC_TYPES = {"specific", "range"}


@pytest.fixture(scope="module")
def investigations() -> pd.DataFrame:
    return load_investigations()


@pytest.fixture(scope="module")
def conditions() -> pd.DataFrame:
    return load_conditions()


def test_investigation_count(investigations: pd.DataFrame) -> None:
    assert len(investigations) == 24
    assert investigations["psi_id"].is_unique
    assert int(investigations["is_core"].sum()) == len(CORE_IDS) == 12


def test_every_record_has_narrative_fields(investigations: pd.DataFrame) -> None:
    for column in ["name", "short_name", "fire_safety_phase", "key_finding", "safety_implication"]:
        assert investigations[column].fillna("").str.len().min() > 0, column


def test_conditions_are_quoted(conditions: pd.DataFrame) -> None:
    numeric = conditions[conditions["point_type"].isin(NUMERIC_TYPES)]
    assert len(numeric) > 0
    for column in ["o2_pct", "pressure_kpa", "flow_cm_s"]:
        documented = numeric[numeric[column].notna()]
        assert documented["source_quote"].fillna("").str.len().min() > 20, column
        assert documented["source_locator"].fillna("").str.len().min() > 3, column


def test_conditions_reference_real_investigations(
    investigations: pd.DataFrame, conditions: pd.DataFrame
) -> None:
    assert set(conditions["investigation_id"]).issubset(set(investigations["psi_id"]))


def test_reviewed_answers_cover_suggested_questions() -> None:
    from tabs.advisor import QUESTIONS

    faq = load_faq()
    assert len(faq) == len(QUESTIONS) == 6
    answers = {item["question"] for item in faq}
    assert set(QUESTIONS) == answers


def test_ranking_is_deterministic_and_coverage_aware(investigations: pd.DataFrame, conditions: pd.DataFrame) -> None:
    records = investigations.to_dict("records")

    first = rank_all(records, conditions, 34.0, 56.5)
    second = rank_all(records, conditions, 34.0, 56.5)
    assert first["score"].tolist() == second["score"].tolist()
    assert first["score"].between(0, 100).all()
    assert first["coverage"].between(0, 100).all()
    assert first["score"].notna().all()


def test_exploration_atmosphere_ranks_documented_match_first(
    investigations: pd.DataFrame, conditions: pd.DataFrame
) -> None:
    ranked = rank_all(investigations.to_dict("records"), conditions, 34.0, 56.5)
    top = ranked.iloc[0]
    assert top["record"]["short_name"] == "ACME BRE"
    assert top["env_label"] == "Exact test match"
    assert top["coverage"] == 100


def test_missing_conditions_lower_coverage_not_score(investigations: pd.DataFrame, conditions: pd.DataFrame) -> None:
    record = investigations[investigations["psi_id"] == "PSI-99"].iloc[0].to_dict()
    score = score_investigation(record, conditions, 34.0, 56.5)
    assert score.parts["environment"] is None
    assert score.coverage < 1.0
    assert sum(score.parts[k] is not None for k in WEIGHTS) < len(WEIGHTS)
