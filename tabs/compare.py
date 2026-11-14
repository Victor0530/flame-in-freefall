"""Compare & Rank tab."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from lib.data import badge, load_investigations, phase_meta


def render() -> None:
    df = load_investigations()
    selected = st.session_state.get("selected", [])

    st.markdown("### Compare & Rank")
    st.caption(
        "Side-by-side evidence for the investigations you selected. Numeric matching and the weighted "
        "evidence-priority score arrive with the curated test conditions."
    )

    if len(selected) < 2:
        st.info(
            "Select at least two investigations in the **Experiment Library** to compare them. "
            f"Currently selected: {len(selected)}."
        )
        if selected:
            rows = df[df["id"].isin(selected)]
            for row in rows.to_dict("records"):
                meta = phase_meta(row["fire_safety_phase"])
                st.markdown(f"- {meta['icon']} **{row['short_name']}** â€” {row['key_finding']}")
        return

    rows = df[df["id"].isin(selected)].to_dict("records")

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
                  <div class="meta">{html.escape(row['facility'])} Â· {html.escape(row['psi_id'])}</div>
                  <div class="lab">Key finding</div>
                  <div class="body">{html.escape(row['key_finding'])}</div>
                  <div class="lab">Implication</div>
                  <div class="body">{html.escape(row['safety_implication'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### Matrix view")
    matrix = pd.DataFrame(
        [
            {
                "Investigation": r["short_name"],
                "Pillar": phase_meta(r["fire_safety_phase"])["label"],
                "Gravity": "Âµg" if r["gravity"] == "microgravity" else "1g",
                "Facility": r["facility"],
                "Materials": r["materials"],
                "Limitation": r["limitations"],
            }
            for r in rows
        ]
    )
    st.dataframe(matrix, width="stretch", hide_index=True)

    st.markdown("#### Evidence-priority score")
    st.caption("Placeholder weights â€” will be applied to curated test conditions, not to metadata.")
    w1, w2, w3 = st.columns(3)
    w1.slider("Directness to your atmosphere", 0.0, 1.0, 0.45, 0.05)
    w2.slider("Flight vs ground evidence", 0.0, 1.0, 0.35, 0.05)
    w3.slider("Recency", 0.0, 1.0, 0.20, 0.05)
    st.warning(
        "Ranking is deliberately disabled until `data/test_conditions.csv` is curated and validated. "
        "Shipping a score over incomplete conditions would be the overclaim this project is meant to avoid."
    )
