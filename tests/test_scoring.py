"""Ranking edge-case tests.

The ranking must stay explainable when weights are zero, data is missing, or a
user picks an atmosphere no experiment tested.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.data import load_conditions, load_investigations  # noqa: E402
from lib.scoring import (  # noqa: E402
    DIMENSION_LABELS,
    WEIGHTS,
    _diagnostics_score,
    _gravity_score,
    _recency_score,
    rank_all,
    score_investigation,
)


@pytest.fixture(scope="module")
def investigations() -> pd.DataFrame:
    return load_investigations()


@pytest.fixture(scope="module")
def conditions() -> pd.DataFrame:
    return load_conditions()


def test_dimension_labels_cover_every_weight() -> None:
    assert set(WEIGHTS) == set(DIMENSION_LABELS)


def test_gravity_scores_are_ordered() -> None:
    assert _gravity_score("microgravity") > _gravity_score("partial gravity") > _gravity_score("1g")


def test_recency_scores_are_monotonic() -> None:
    assert _recency_score(2020) > _recency_score(2010) > _recency_score(1995)
    assert _recency_score(float("nan")) == 0.4


def test_diagnostics_cap_at_five_variables() -> None:
    assert _diagnostics_score("") == 0
    assert _diagnostics_score("a; b") == pytest.approx(0.4)
    assert _diagnostics_score("a;b;c;d;e;f") == 1.0


def test_zero_weights_do_not_divide_by_zero(investigations: pd.DataFrame, conditions: pd.DataFrame) -> None:
    record = investigations.iloc[0].to_dict()
    zero = {key: 0.0 for key in WEIGHTS}
    score = score_investigation(record, conditions, 34.0, 56.5, zero)
    assert score.total == 0.0
    assert score.coverage == 0.0


def test_missing_environment_reduces_coverage(
    investigations: pd.DataFrame, conditions: pd.DataFrame
) -> None:
    record = investigations[investigations["psi_id"] == "PSI-99"].iloc[0].to_dict()
    score = score_investigation(record, conditions, 34.0, 56.5)
    assert score.parts["environment"] is None
    assert 0 < score.coverage < 1


def test_ground_only_record_gets_low_gravity_score(
    investigations: pd.DataFrame, conditions: pd.DataFrame
) -> None:
    record = investigations[investigations["gravity"] == "1g"].iloc[0].to_dict()
    score = score_investigation(record, conditions, 21.0, 101.3)
    assert score.parts["gravity"] == pytest.approx(0.15)


def test_rank_all_handles_empty_input_and_bad_weights(conditions: pd.DataFrame) -> None:
    assert rank_all([], conditions, 34.0, 56.5).empty
    ranked = rank_all([], conditions, 34.0, 56.5, {"environment": 0.0})
    assert ranked.empty


def test_rank_all_clamps_scores_and_coverage(investigations: pd.DataFrame, conditions: pd.DataFrame) -> None:
    ranked = rank_all(investigations.to_dict("records"), conditions, 34.0, 56.5)
    assert ranked["score"].between(0, 100).all()
    assert ranked["coverage"].between(0, 100).all()
    assert ranked["score"].is_monotonic_decreasing


def test_custom_atmosphere_changes_ranking(investigations: pd.DataFrame, conditions: pd.DataFrame) -> None:
    records = investigations.to_dict("records")
    exploration = rank_all(records, conditions, 34.0, 56.5)
    sea_level = rank_all(records, conditions, 21.0, 101.4)
    assert exploration.iloc[0]["record"]["short_name"] == "ACME BRE"
    assert sea_level.iloc[0]["record"]["short_name"] == "ACME BRE"
    assert exploration.iloc[0]["env_label"] == "Exact test match"
    assert sea_level.iloc[0]["env_label"] == "Exact test match"
    assert exploration.iloc[0]["reason"] != sea_level.iloc[0]["reason"]
