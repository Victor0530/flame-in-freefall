"""Transparent, evidence-based ranking for a habitat atmosphere.

The score ranks how directly an investigation supports a fire-safety decision for a
given oxygen/pressure environment. It is not a flammability prediction and it never
fills a missing condition with an assumed value: dimensions with no documented data
are dropped from the weighting and reported as reduced coverage instead.

Every input is either metadata from the PSI record or a quoted condition row in
data/test_conditions.csv.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

# Default weights. Users can move them in the UI; the ranking renormalises over the
# dimensions that have data for each investigation.
WEIGHTS = {
    "environment": 0.45,
    "gravity": 0.30,
    "flow": 0.10,
    "diagnostics": 0.10,
    "recency": 0.05,
}

DIMENSION_LABELS = {
    "environment": "Atmosphere match",
    "gravity": "Microgravity evidence",
    "flow": "Flow characterisation",
    "diagnostics": "Diagnostics breadth",
    "recency": "Recency",
}


@dataclass
class Score:
    total: float
    coverage: float
    parts: dict[str, float | None] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    env_label: str = ""


def _environment_score(
    rows: pd.DataFrame, o2_pct: float, pressure_kpa: float
) -> tuple[float | None, str, str]:
    """Return (0-1 score, reason, short label). None means no documented numeric condition."""
    if rows.empty:
        return None, "no numeric test conditions published", "No numeric conditions"

    numeric = rows[rows["o2_pct"].notna()].copy()
    if numeric.empty:
        return None, "conditions described qualitatively only", "Qualitative only"

    specific = numeric[numeric["point_type"] == "specific"]
    if not specific.empty:
        o2_gap = (specific["o2_pct"] - o2_pct).abs()
        with_p = specific[specific["pressure_kpa"].notna()].copy()
        if not with_p.empty:
            both = with_p[
                ((with_p["o2_pct"] - o2_pct).abs() <= 1.0)
                & ((with_p["pressure_kpa"] - pressure_kpa).abs() <= 3.0)
            ]
            if not both.empty:
                row = both.iloc[0]
                return (
                    1.0,
                    f"tested at {row['o2_pct']:.1f}% O2 / {row['pressure_kpa']:.1f} kPa, "
                    "which matches the target atmosphere",
                    "Exact test match",
                )
        close = specific[o2_gap <= 3.0]
        if not close.empty:
            row = close.iloc[0]
            return (
                0.75,
                f"tested within 3 points of the target O2 fraction ({row['o2_pct']:.1f}%)",
                "Nearby O2 fraction",
            )

    spans_o2 = (numeric["o2_pct"].min() <= o2_pct <= numeric["o2_pct"].max())
    spans_p = True
    if numeric["pressure_kpa"].notna().any():
        spans_p = numeric["pressure_kpa"].min() <= pressure_kpa <= numeric["pressure_kpa"].max()
    if spans_o2 and spans_p:
        return 0.8, "documented test range spans the target atmosphere", "Range spans target"
    if spans_o2 or spans_p:
        return 0.5, "documented range overlaps part of the target atmosphere", "Partial overlap"
    return 0.3, "tested at a different atmosphere from the target", "Different atmosphere"


def _gravity_score(gravity: str) -> float:
    g = (gravity or "").lower()
    if g == "microgravity":
        return 1.0
    if "low" in g or "partial" in g or "drop" in g:
        return 0.6
    return 0.15


def _flow_score(rows: pd.DataFrame) -> float:
    if not rows.empty and rows["flow_cm_s"].notna().any():
        return 1.0
    return 0.3


def _diagnostics_score(measured: str) -> float:
    count = len([p for p in (measured or "").split(";") if p.strip()])
    return min(1.0, count / 5)


def _recency_score(year_end: float | None) -> float:
    if pd.isna(year_end):
        return 0.4
    if year_end >= 2015:
        return 1.0
    if year_end >= 2005:
        return 0.7
    return 0.4


def score_investigation(
    record: dict,
    conditions: pd.DataFrame,
    o2_pct: float,
    pressure_kpa: float,
    weights: dict[str, float] | None = None,
) -> Score:
    w = weights or WEIGHTS
    rows = conditions[conditions["investigation_id"] == record["psi_id"]]

    env, env_reason, env_label = _environment_score(rows, o2_pct, pressure_kpa)
    parts = {
        "environment": env,
        "gravity": _gravity_score(record.get("gravity", "")),
        "flow": _flow_score(rows),
        "diagnostics": _diagnostics_score(record.get("measured_variables", "")),
        "recency": _recency_score(record.get("year_end")),
    }

    used = {k: v for k, v in parts.items() if v is not None}
    weight_total = sum(w[k] for k in used)
    if weight_total <= 0:
        return Score(0.0, 0.0, parts, [env_reason], env_label)

    total = sum(w[k] * v for k, v in used.items()) / weight_total
    coverage = weight_total / sum(w.values())

    reasons = [env_reason]
    if parts["gravity"] == 1.0:
        reasons.append("microgravity data from flight")
    elif parts["gravity"] <= 0.2:
        reasons.append("ground-only or modelling evidence")
    if parts["flow"] == 1.0:
        reasons.append("forced-flow condition quantified")
    if parts["recency"] == 1.0:
        reasons.append("recent programme (ended 2015 or later)")
    if env is None:
        reasons.append("atmosphere coverage counted as unknown, not as a failure")

    return Score(total, coverage, parts, reasons, env_label)


def rank_all(
    records: list[dict],
    conditions: pd.DataFrame,
    o2_pct: float,
    pressure_kpa: float,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    out = []
    for record in records:
        s = score_investigation(record, conditions, o2_pct, pressure_kpa, weights)
        out.append(
            {
                "score": round(s.total * 100),
                "coverage": round(s.coverage * 100),
                "reason": s.reasons[0],
                "env_label": s.env_label,
                "parts": s.parts,
                "reasons": s.reasons,
                "record": record,
            }
        )
    frame = pd.DataFrame(out)
    if frame.empty:
        return frame
    return frame.sort_values(["score", "coverage"], ascending=False).reset_index(drop=True)
