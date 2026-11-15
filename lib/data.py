"""Shared data access for the Flame in Freefall dashboard."""

from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

CORE_IDS = [
    "bass", "bass-ii",
    "saffire-i", "saffire-ii", "saffire-iii",
    "flex", "flex-2",
    "same", "same-r",
    "acme-bre", "acme-cfi-g", "spice",
]

PHASES = {
    "prevention": {"label": "Prevention", "icon": "🛡️", "color": "#ff8a3d"},
    "detection": {"label": "Detection", "icon": "📡", "color": "#4cc9f0"},
    "suppression": {"label": "Suppression", "icon": "🧯", "color": "#b388ff"},
}

PRESETS = {
    "Earth sea level": (20.9, 101.4),
    "ISS cabin": (21.0, 101.3),
    "Exploration (34% / 8.2 psia)": (34.0, 56.5),
    "Apollo-era 5 psi": (100.0, 34.5),
    "EMU suit (4.3 psia)": (100.0, 29.6),
}

DESTINATIONS = {
    "Moon habitat": {
        "preset": "Exploration (34% / 8.2 psia)",
        "caption": "34% O₂ / 8.2 psia exploration atmosphere",
    },
    "Mars transit": {
        "preset": "Exploration (34% / 8.2 psia)",
        "caption": "34% O₂ / 8.2 psia exploration atmosphere",
    },
    "ISS (current)": {
        "preset": "ISS cabin",
        "caption": "21% O₂ / 14.7 psia cabin air",
    },
    "EMU spacesuit": {
        "preset": "EMU suit (4.3 psia)",
        "caption": "100% O₂ / 4.3 psia",
    },
}

# NASA-STD-6001B, Test 1 historical test point.
STD_O2_PCT = 30.0
STD_PRESSURE_KPA = 70.3
STD_PPO2_KPA = STD_O2_PCT / 100 * STD_PRESSURE_KPA  # 21.1 kPa

EXPLORATION_PPO2_KPA = 0.34 * 56.5  # 19.2 kPa

MATERIAL_KEYWORDS = {
    "Fabrics": ["fabric", "cloth", "cotton", "nomex", "sibal", "textile", "felt"],
    "Plastics": ["plastic", "pmma", "acrylic", "polymer", "polyethylene", "polypropylene", "pc"],
    "Electronics": ["wire", "circuit", "pcb", "electronic", "cable", "connector"],
    "Paper / packaging": ["paper", "cellulose", "cardboard", "packaging"],
    "Liquids / fuels": ["fuel", "droplet", "liquid", "heptane", "methanol", "dodecane", "ethanol"],
}


@st.cache_data(show_spinner=False)
def load_investigations() -> pd.DataFrame:
    path = DATA / "investigations.csv"
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["year_start"] = pd.to_numeric(df["year_start"], errors="coerce")
    df["year_end"] = pd.to_numeric(df["year_end"], errors="coerce")
    df["is_core"] = df["id"].isin(CORE_IDS)
    df["phase_order"] = df["fire_safety_phase"].map(
        {"prevention": 0, "detection": 1, "suppression": 2}
    ).fillna(3).astype(int)
    return df.sort_values(
        ["gravity", "phase_order", "is_core", "year_start"],
        ascending=[False, True, False, False],
    ).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_conditions() -> pd.DataFrame:
    path = DATA / "test_conditions.csv"
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for col in ("o2_pct", "pressure_kpa", "flow_cm_s"):
        df[col] = pd.to_numeric(df[col].replace("", pd.NA), errors="coerce")
    return df


def matches_materials(text: str, selected: list[str]) -> bool:
    if not selected:
        return True
    haystack = (text or "").lower()
    return any(k in haystack for label in selected for k in MATERIAL_KEYWORDS.get(label, []))


def filter_records(
    df: pd.DataFrame,
    *,
    pillar: str = "All",
    program: str = "All",
    flight_only: bool = False,
    query: str = "",
    materials: list[str] | None = None,
    focus_materials: bool = False,
) -> pd.DataFrame:
    """Apply the library filters. Kept here so the behaviour is testable."""
    view = df.copy()
    if pillar != "All":
        view = view[view["fire_safety_phase"] == pillar.lower()]
    if program != "All":
        view = view[view["program"] == program]
    if flight_only:
        view = view[view["gravity"] == "microgravity"]

    focus = materials or []
    if focus_materials and focus:
        mask = view.apply(
            lambda r: matches_materials(
                f"{r['materials']} {r['name']} {r['objective']}", focus
            ),
            axis=1,
        )
        if mask.any():
            view = view[mask]

    if query.strip():
        q = query.strip().lower()
        columns = [
            "short_name",
            "name",
            "materials",
            "key_finding",
            "safety_implication",
            "measured_variables",
            "objective",
        ]
        mask = view.apply(
            lambda r: q in " ".join(str(r[c]) for c in columns).lower(), axis=1
        )
        view = view[mask]
    return view


def year_range(row) -> str:
    ys = pd.notna(row.get("year_start"))
    ye = pd.notna(row.get("year_end"))
    if ys and ye:
        return f"{int(row['year_start'])}–{int(row['year_end'])}"
    if ys:
        return f"{int(row['year_start'])}"
    if ye:
        return f"–{int(row['year_end'])}"
    return "dates not published"


@st.cache_data(show_spinner=False)
def load_faq() -> list[dict]:
    path = DATA / "faq.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("items", [])
    except (json.JSONDecodeError, OSError):
        return []


@st.cache_data(show_spinner=False)
def corpus_stats() -> dict:
    """Small runtime summary used in the sidebar; never loads the whole index."""
    path = DATA / "corpus" / "chunks.jsonl"
    if not path.exists():
        return {"passages": 0, "words": 0}
    passages = 0
    words = 0
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            passages += 1
            try:
                words += len(json.loads(line).get("text", "").split())
            except json.JSONDecodeError:
                continue
    except OSError:
        return {"passages": 0, "words": 0}
    return {"passages": passages, "words": words}


def phase_meta(phase: str) -> dict:
    return PHASES.get(phase, {"label": phase.title(), "icon": "•", "color": "#8b93a7"})


def badge(text: str, color: str) -> str:
    return (
        f'<span style="display:inline-block;padding:2px 9px;border-radius:999px;'
        f'background:{color}22;border:1px solid {color}66;color:{color};'
        f'font-size:0.72rem;font-weight:600;letter-spacing:.02em;">{html.escape(str(text))}</span>'
    )


def evidence_counts(df: pd.DataFrame) -> dict:
    return {
        "total": len(df),
        "flight": int((df["gravity"] == "microgravity").sum()),
        "core": int(df["is_core"].sum()),
        "reviewed": int((df["reviewed"].str.lower() == "true").sum()),
        "pillars": int(df["fire_safety_phase"].nunique()),
    }
