"""Shared data access for the Flame in Freefall dashboard."""

from __future__ import annotations

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

# NASA-STD-6001B, Test 1 historical test point.
STD_O2_PCT = 30.0
STD_PRESSURE_KPA = 70.3
STD_PPO2_KPA = STD_O2_PCT / 100 * STD_PRESSURE_KPA  # 21.1 kPa

EXPLORATION_PPO2_KPA = 0.34 * 56.5  # 19.2 kPa


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
    return df.sort_values(["gravity", "phase_order", "year_start"], ascending=[True, True, True])


def phase_meta(phase: str) -> dict:
    return PHASES.get(phase, {"label": phase.title(), "icon": "•", "color": "#8b93a7"})


def badge(text: str, color: str) -> str:
    return (
        f'<span style="display:inline-block;padding:2px 9px;border-radius:999px;'
        f'background:{color}22;border:1px solid {color}66;color:{color};'
        f'font-size:0.72rem;font-weight:600;letter-spacing:.02em;">{text}</span>'
    )


def evidence_counts(df: pd.DataFrame) -> dict:
    return {
        "total": len(df),
        "flight": int((df["gravity"] == "microgravity").sum()),
        "core": int(df["is_core"].sum()),
        "reviewed": int((df["reviewed"].str.lower() == "true").sum()),
    }
