"""Experiment Library tab."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from lib.data import badge, load_investigations, phase_meta


def _card(row, selected: list[str]) -> None:
    meta = phase_meta(row["fire_safety_phase"])
    years = ""
    ys = pd.notna(row["year_start"])
    ye = pd.notna(row["year_end"])
    if ys and ye:
        years = f"{int(row['year_start'])}-{int(row['year_end'])}"
    elif ys:
        years = f"{int(row['year_start'])}"
    elif ye:
        years = f"-{int(row['year_end'])}"

    tags = badge(f"{meta['icon']} {meta['label']}", meta["color"])
    if row["gravity"] == "microgravity":
        tags += badge("Flight", "#7ee787")
    else:
        tags += badge("Ground", "#8b93a7")
    if row["is_core"]:
        tags += badge("Core", "#ffc46b")

    st.markdown(
        f"""
        <div class="card">
          <div>{tags}</div>
          <h4>{html.escape(row['short_name'])}</h4>
          <div class="full">{html.escape(row['name'])}</div>
          <div class="meta">{html.escape(row['facility'] or '—')} &nbsp;·&nbsp; {html.escape(years or 'dates n/a')} &nbsp;·&nbsp; {html.escape(row['psi_id'])}</div>
          <div class="lab">Key finding</div>
          <div class="body">{html.escape(row['key_finding'])}</div>
          <div class="lab">Safety implication</div>
          <div class="body">{html.escape(row['safety_implication'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    in_compare = row["id"] in selected
    with cols[0]:
        if st.button(
            "Compare +" if not in_compare else "Added ✓",
            key=f"add_{row['id']}",
            disabled=in_compare or len(selected) >= 4,
            width="stretch",
        ):
            selected.append(row["id"])
            st.session_state["selected"] = selected
            st.toast(f"Added {row['short_name']} to comparison")
            st.rerun()
    with cols[1]:
        st.link_button("PSI record ↗", row["psi_url"], width="stretch")

    with st.expander("Details & limits"):
        st.markdown(f"**Objective.** {row['objective']}")
        st.markdown(f"**Materials.** {row['materials']}")
        st.markdown(f"**Measured.** {row['measured_variables']}")
        st.markdown(f"**Limitations.** {row['limitations']}")
        st.caption(
            f"Confidence: {row['confidence']} · reviewed: {row['reviewed']} · {row['notes']}"
        )


def render() -> None:
    df = load_investigations()
    selected = st.session_state.setdefault("selected", [])

    st.markdown("### Experiment Library")
    st.caption(
        "Every public PSI combustion investigation, tagged by fire-safety pillar. "
        "Metadata is pulled live from the PSI repository; numeric conditions are curated separately."
    )

    pillar = st.segmented_control(
        "Fire-safety pillar", ["All", "Prevention", "Detection", "Suppression"], default="All"
    ) or "All"

    c1, c2, c3 = st.columns([1.3, 2.6, 1.1])
    with c1:
        program = st.selectbox("Program", ["All"] + sorted(df["program"].unique().tolist()))
    with c2:
        query = st.text_input("Search", placeholder="materials, soot, oxygen, smoke, droplet …")
    with c3:
        flight_only = st.toggle("Flight", value=True, help="Show flight experiments only")

    view = df.copy()
    if pillar != "All":
        view = view[view["fire_safety_phase"] == pillar.lower()]
    if program != "All":
        view = view[view["program"] == program]
    if flight_only:
        view = view[view["gravity"] == "microgravity"]
    if query:
        q = query.lower()
        mask = view.apply(
            lambda r: q in " ".join(
                str(r[c]) for c in ["short_name", "name", "materials", "key_finding",
                                    "safety_implication", "measured_variables", "objective"]
            ).lower(),
            axis=1,
        )
        view = view[mask]

    st.caption(
        f"{len(view)} of {len(df)} records · {int(view['is_core'].sum())} core · "
        f"{int((view['gravity'] == 'microgravity').sum())} flight"
    )

    if view.empty:
        st.info("No investigations match these filters. Widen the pillar or clear the search.")
        return

    rows = view.to_dict("records")
    for i in range(0, len(rows), 2):
        left, right = st.columns(2, gap="medium")
        with left:
            _card(rows[i], selected)
        if i + 1 < len(rows):
            with right:
                _card(rows[i + 1], selected)
