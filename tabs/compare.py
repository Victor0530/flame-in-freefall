"""Compare & Rank tab."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from lib.data import PRESETS, badge, load_conditions, load_investigations, phase_meta
from lib.scoring import DIMENSION_LABELS, WEIGHTS, rank_all

NUMERIC_TYPES = {"specific", "range"}

WEIGHT_PRESETS = {
    "Balanced": WEIGHTS,
    "Atmosphere first": {
        "environment": 0.65,
        "gravity": 0.25,
        "flow": 0.05,
        "diagnostics": 0.03,
        "recency": 0.02,
    },
    "Flight evidence first": {
        "environment": 0.30,
        "gravity": 0.55,
        "flow": 0.07,
        "diagnostics": 0.06,
        "recency": 0.02,
    },
}


def _set_weights(values: dict[str, float]) -> None:
    for key, value in values.items():
        st.session_state[f"w_{key}"] = float(value)


def _weights_from_ui() -> dict[str, float]:
    st.markdown("**Dimension weights**")
    cols = st.columns(5)
    values = {}
    for col, (key, default) in zip(cols, WEIGHTS.items()):
        values[key] = col.slider(
            DIMENSION_LABELS[key], 0.0, 1.0, default, 0.05, key=f"w_{key}"
        )

    bar = st.columns(len(WEIGHT_PRESETS))
    for col, (label, preset) in zip(bar, WEIGHT_PRESETS.items()):
        with col:
            st.button(
                label,
                key=f"weight_preset_{label}",
                on_click=_set_weights,
                args=(preset,),
                width="stretch",
            )

    if sum(values.values()) == 0:
        st.warning("Every weight is zero, so the ranking cannot separate investigations.")
        return WEIGHTS
    return values


def _selected_cards(rows: list[dict], selected: list[str]) -> None:
    if not rows:
        st.info(
            "No investigations in the tray yet. Add up to four from the **Library**, "
            "then return here to compare them side by side."
        )
        return

    st.markdown("### Selected evidence")
    cols = st.columns(len(rows))
    for col, row in zip(cols, rows):
        meta = phase_meta(row["fire_safety_phase"])
        with col:
            st.markdown(
                f"""
                <div class="card">
                  <div>{badge(meta['label'], meta['color'])}{badge('Flight' if row['gravity']=='microgravity' else 'Ground', '#8b93a7')}</div>
                  <h4>{html.escape(row['short_name'])}</h4>
                  <div class="meta">{html.escape(row['facility'] or 'Facility not published')} · {html.escape(row['psi_id'])}</div>
                  <div class="lab">Key finding</div>
                  <div class="body">{html.escape(row['key_finding'])}</div>
                  <div class="lab">Implication</div>
                  <div class="body">{html.escape(row['safety_implication'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Remove", key=f"rm_{row['id']}", width="stretch"):
                st.session_state["selected"] = [i for i in selected if i != row["id"]]
                st.rerun()

    if len(rows) == 1:
        st.caption("Add a second investigation to compare the two cards side by side.")


def _atmosphere() -> tuple[str, float, float]:
    options = list(PRESETS) + ["Custom"]
    preset_name = st.selectbox(
        "Rank evidence against this atmosphere",
        options,
        index=options.index("Exploration (34% / 8.2 psia)"),
        help="Presets come from NASA-STD-6001B and published exploration-atmosphere values.",
        key="rank_atmosphere",
    )
    if preset_name == "Custom":
        c1, c2 = st.columns(2)
        o2_pct = c1.number_input(
            "O₂ fraction (%)", min_value=5.0, max_value=100.0, value=34.0, step=0.5, key="rank_o2"
        )
        pressure_kpa = c2.number_input(
            "Total pressure (kPa)", min_value=10.0, max_value=101.4, value=56.5, step=0.1, key="rank_pressure"
        )
        label = "Custom"
    else:
        o2_pct, pressure_kpa = PRESETS[preset_name]
        label = preset_name

    st.markdown(
        f"Target: **{o2_pct:.1f}% O₂ at {pressure_kpa:.1f} kPa** "
        f"(ppO₂ {o2_pct / 100 * pressure_kpa:.1f} kPa)"
    )
    return label, float(o2_pct), float(pressure_kpa)


def render() -> None:
    df = load_investigations()
    cond = load_conditions()
    selected = st.session_state.get("selected", [])

    st.markdown("## Compare & Rank")
    st.caption(
        "Rank the documented evidence against a specific habitat atmosphere. The score measures how "
        "directly an investigation supports a fire-safety decision — it is not a flammability prediction."
    )

    _, o2_pct, pressure_kpa = _atmosphere()

    flights_only = st.toggle("Flight experiments only", value=True, key="rank_flights_only")

    rows = df[df["id"].isin(selected)].to_dict("records")
    _selected_cards(rows, selected)

    with st.expander("How the score is calculated", expanded=False):
        st.markdown(
            "Each investigation is scored on five documented dimensions. Missing data is **dropped** "
            "from the weighted average and reported as *coverage* — it is never replaced by an assumption.\n\n"
            "| Dimension | Question it answers |\n|---|---|\n"
            "| Atmosphere match | Did this experiment run at, or span, your O₂ fraction and pressure? |\n"
            "| Microgravity evidence | Flight data, partial gravity, or ground only? |\n"
            "| Flow characterisation | Is the forced-flow condition quantified? |\n"
            "| Diagnostics breadth | How many measured variables does the record document? |\n"
            "| Recency | How current is the programme? |"
        )
        weights = _weights_from_ui()

    pool = df[df["gravity"] == "microgravity"] if flights_only else df
    ranked = rank_all(pool.to_dict("records"), cond, o2_pct, pressure_kpa, weights)

    st.markdown("### Evidence ranking")
    ranked_records = ranked.to_dict("records")
    table = pd.DataFrame(
        {
            "#": range(1, len(ranked) + 1),
            "Investigation": [
                ("★ " if r["record"]["is_core"] else "") + r["record"]["short_name"]
                for r in ranked_records
            ],
            "Pillar": [phase_meta(r["record"]["fire_safety_phase"])["label"] for r in ranked_records],
            "Score": ranked["score"],
            "Coverage %": ranked["coverage"],
            "Atmosphere evidence": ranked["env_label"],
            "Why": ranked["reason"],
            "Tray": ["✓" if r["record"]["id"] in selected else "" for r in ranked_records],
        }
    )
    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        height=min(560, 42 + 30 * len(table)),
        column_config={
            "#": st.column_config.NumberColumn(width="small"),
            "Score": st.column_config.ProgressColumn(format="%d", min_value=0, max_value=100, width="medium"),
            "Coverage %": st.column_config.NumberColumn(format="%d%%", width="small"),
            "Atmosphere evidence": st.column_config.TextColumn(width="medium"),
            "Tray": st.column_config.TextColumn(width="small"),
        },
    )
    st.download_button(
        "Download ranking (CSV)",
        table.to_csv(index=False).encode("utf-8"),
        "flame-in-freefall-ranking.csv",
        "text/csv",
    )

    documented = int(cond[cond["point_type"].isin(NUMERIC_TYPES)]["investigation_id"].nunique())
    st.caption(
        f"{documented} of {len(df)} investigations have numeric conditions in the curated table. "
        "Rows with lower coverage are ranked on fewer dimensions — read coverage before trusting a rank."
    )

    st.markdown("### Condition matrix")
    matrix = cond[cond["investigation_id"].isin(pool["psi_id"])].copy()
    if matrix.empty:
        st.info("No curated conditions for this selection.")
    else:
        names = df.set_index("psi_id")["short_name"]
        view = pd.DataFrame(
            {
                "Investigation": matrix["short_name"].fillna(
                    matrix["investigation_id"].map(names)
                ),
                "Condition": matrix["point_label"],
                "Type": matrix["point_type"],
                "g": matrix["gravity"],
                "O₂ %": matrix["o2_pct"],
                "Pressure kPa": matrix["pressure_kpa"],
                "Flow cm/s": matrix["flow_cm_s"],
                "Source": matrix["source_locator"],
                "Quote": matrix["source_quote"].str.slice(0, 140),
            }
        )
        st.dataframe(
            view,
            width="stretch",
            hide_index=True,
            column_config={"Quote": st.column_config.TextColumn(width="large")},
        )
        st.download_button(
            "Download condition matrix (CSV)",
            view.to_csv(index=False).encode("utf-8"),
            "flame-in-freefall-conditions.csv",
            "text/csv",
        )
        st.caption(
            "Every numeric cell is copied from the quoted source text. Blank cells mean the source does not "
            "publish that value — they are not zeros."
        )

    st.markdown("### What this ranking does not tell you")
    st.markdown(
        "- It does **not** say a material is safe or unsafe at your atmosphere.\n"
        "- It does **not** translate 1-g screening results into microgravity behaviour.\n"
        "- A high score means *better-documented evidence*, not a lower fire risk.\n"
        "- Where NASA has not published numeric conditions, absence of evidence is shown, not scored as a failure."
    )
