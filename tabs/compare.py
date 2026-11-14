"""Compare & Rank tab."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from lib.data import PRESETS, badge, load_conditions, load_investigations, phase_meta
from lib.scoring import DIMENSION_LABELS, WEIGHTS, rank_all

NUMERIC_TYPES = {"specific", "range"}


def _weights_from_ui() -> dict[str, float]:
    st.markdown("###### Dimension weights")
    cols = st.columns(5)
    values = {}
    for col, (key, default) in zip(cols, WEIGHTS.items()):
        values[key] = col.slider(
            DIMENSION_LABELS[key], 0.0, 1.0, default, 0.05, key=f"w_{key}"
        )
    if sum(values.values()) == 0:
        st.warning("Every weight is zero, so the ranking cannot separate investigations.")
        return WEIGHTS
    return values


def render() -> None:
    df = load_investigations()
    cond = load_conditions()
    selected = st.session_state.get("selected", [])

    st.markdown("### Compare & Rank")
    st.caption(
        "Rank the documented evidence against a specific habitat atmosphere. The score measures how "
        "directly an investigation supports a fire-safety decision — it is not a flammability prediction."
    )

    preset_name = st.selectbox(
        "Rank evidence against this atmosphere",
        list(PRESETS),
        index=list(PRESETS).index("Exploration (34% / 8.2 psia)"),
        help="Presets come from NASA-STD-6001B and published exploration-atmosphere values.",
    )
    o2_pct, pressure_kpa = PRESETS[preset_name]
    st.markdown(
        f"Target: **{o2_pct:.1f}% O₂ at {pressure_kpa:.1f} kPa** "
        f"(ppO₂ {o2_pct / 100 * pressure_kpa:.1f} kPa)"
    )

    flights_only = st.toggle("Flight experiments only", value=True)

    if selected:
        rows = df[df["id"].isin(selected)].to_dict("records")
        if len(rows) >= 2:
            st.markdown("#### Selected evidence")
            cols = st.columns(len(rows))
            for col, row in zip(cols, rows):
                meta = phase_meta(row["fire_safety_phase"])
                with col:
                    st.markdown(
                        f"""
                        <div class="card">
                          <div>{badge(meta['label'], meta['color'])}{badge('Flight' if row['gravity']=='microgravity' else 'Ground', '#8b93a7')}</div>
                          <h4>{html.escape(row['short_name'])}</h4>
                          <div class="meta">{html.escape(row['facility'])} · {html.escape(row['psi_id'])}</div>
                          <div class="lab">Key finding</div>
                          <div class="body">{html.escape(row['key_finding'])}</div>
                          <div class="lab">Implication</div>
                          <div class="body">{html.escape(row['safety_implication'])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Select at least two investigations in the **Experiment Library** for the side-by-side cards.")

    weights = WEIGHTS
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

    st.markdown("#### Evidence ranking")
    table = pd.DataFrame(
        {
            "#": range(1, len(ranked) + 1),
            "Investigation": [
                ("★ " if r["record"]["is_core"] else "") + r["record"]["short_name"]
                for r in ranked.to_dict("records")
            ],
            "Pillar": [phase_meta(r["record"]["fire_safety_phase"])["label"] for r in ranked.to_dict("records")],
            "Score": ranked["score"],
            "Coverage %": ranked["coverage"],
            "Atmosphere evidence": ranked["env_label"],
            "Why": ranked["reason"],
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
        },
    )

    documented = int(cond[cond["point_type"].isin(NUMERIC_TYPES)]["investigation_id"].nunique())
    st.caption(
        f"{documented} of {len(df)} investigations have numeric conditions in the curated table. "
        "Rows with lower coverage are ranked on fewer dimensions — read coverage before trusting a rank."
    )

    st.markdown("#### Condition matrix")
    matrix = cond[cond["investigation_id"].isin(pool["psi_id"])].copy()
    if matrix.empty:
        st.info("No curated conditions for this selection.")
    else:
        matrix = matrix.merge(
            df[["psi_id", "short_name"]], left_on="investigation_id", right_on="psi_id", how="left"
        )
        view = pd.DataFrame(
            {
                "Investigation": matrix["short_name_y"].fillna(matrix["short_name_x"]).fillna(matrix["investigation_id"]),
                "Condition": matrix["point_label"],
                "Type": matrix["point_type"],
                "g": matrix["gravity"],
                "O₂ %": matrix["o2_pct"],
                "Pressure kPa": matrix["pressure_kpa"],
                "Flow cm/s": matrix["flow_cm_s"],
                "Source": matrix["source_locator"],
                "Quote": matrix["source_quote"].str.slice(0, 90),
            }
        )
        st.dataframe(view, width="stretch", hide_index=True)
        st.caption(
            "Every numeric cell is copied from the quoted source text. Blank cells mean the source does not "
            "publish that value — they are not zeros."
        )

    st.markdown("#### What this ranking does not tell you")
    st.markdown(
        "- It does **not** say a material is safe or unsafe at your atmosphere.\n"
        "- It does **not** translate 1-g screening results into microgravity behaviour.\n"
        "- A high score means *better-documented evidence*, not a lower fire risk.\n"
        "- Where NASA has not published numeric conditions, absence of evidence is shown, not scored as a failure."
    )
