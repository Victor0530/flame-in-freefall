"""Experiment Library tab."""

from __future__ import annotations

import html

import streamlit as st

from lib.data import (
    badge,
    filter_records,
    load_investigations,
    phase_meta,
    year_range,
)

FILTER_DEFAULTS = {
    "lib_pillar": "All",
    "lib_program": "All",
    "lib_query": "",
    "lib_flight": False,
    "lib_materials": False,
}


def _clear_filters() -> None:
    for key, value in FILTER_DEFAULTS.items():
        st.session_state[key] = value


def _or(value: str, fallback: str = "Not published in the public record.") -> str:
    value = (value or "").strip()
    return value if value else fallback


def _card(row, selected: list[str]) -> None:
    meta = phase_meta(row["fire_safety_phase"])
    tags = badge(f"{meta['icon']} {meta['label']}", meta["color"])
    tags += badge("Flight", "#7ee787") if row["gravity"] == "microgravity" else badge("Ground", "#8b93a7")
    if row["is_core"]:
        tags += badge("Core", "#ffc46b")
    if row["program"] and row["program"] != "PSI":
        tags += badge(row["program"], "#4cc9f0")

    st.markdown(
        f"""
        <div class="card">
          <div>{tags}</div>
          <h3>{html.escape(row['short_name'])}</h3>
          <div class="full">{html.escape(row['name'])}</div>
          <div class="meta">{html.escape(row['facility'] or 'Facility not published')} &nbsp;·&nbsp;
          {html.escape(year_range(row))} &nbsp;·&nbsp; {html.escape(row['psi_id'])}</div>
          <div class="lab">Key finding</div>
          <div class="body">{html.escape(_or(row['key_finding']))}</div>
          <div class="lab">Safety implication</div>
          <div class="body">{html.escape(_or(row['safety_implication']))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    in_compare = row["id"] in selected
    with cols[0]:
        if st.button(
            "Added ✓" if in_compare else "Compare +",
            key=f"add_{row['id']}",
            disabled=in_compare or len(selected) >= 4,
            width="stretch",
            help=(
                "Already in the comparison tray"
                if in_compare
                else "Tray is full — clear it in the sidebar"
                if len(selected) >= 4
                else "Add to the comparison tray"
            ),
        ):
            selected.append(row["id"])
            st.session_state["selected"] = selected
            st.toast(f"Added {row['short_name']} to the comparison tray")
            st.rerun()
    with cols[1]:
        if row.get("psi_url"):
            st.link_button("PSI record ↗", row["psi_url"], width="stretch")
        else:
            st.button("PSI link unavailable", disabled=True, width="stretch")

    with st.expander("Details, measurements and limits"):
        st.markdown(f"**Objective.** {_or(row['objective'])}")
        st.markdown(f"**Materials.** {_or(row['materials'])}")
        st.markdown(f"**Measured variables.** {_or(row['measured_variables'])}")
        st.markdown(f"**Limitations.** {_or(row['limitations'])}")
        if row.get("ntrs_url"):
            st.markdown(f"[NTRS record ↗]({row['ntrs_url']})")
        st.caption(
            f"Confidence: {_or(row['confidence'], 'not stated')} · "
            f"Reviewed: {_or(row['reviewed'], 'not stated')} · {_or(row['notes'], 'No curator note.')}"
        )


def render() -> None:
    df = load_investigations()
    selected = st.session_state.setdefault("selected", [])

    st.markdown("## Experiment Library")
    st.caption(
        "Every public PSI combustion investigation, tagged by fire-safety pillar. "
        "PSI metadata is the source; numeric conditions are curated separately in Compare."
    )

    pillar = st.segmented_control(
        "Fire-safety pillar",
        ["All", "Prevention", "Detection", "Suppression"],
        default="All",
        key="lib_pillar",
    ) or "All"

    c1, c2, c3 = st.columns([1.2, 2.4, 1.5])
    with c1:
        program = st.selectbox(
            "Program",
            ["All"] + sorted(df["program"].unique().tolist()),
            key="lib_program",
        )
    with c2:
        query = st.text_input(
            "Search",
            placeholder="materials, soot, oxygen, smoke, droplet …",
            key="lib_query",
        )
    with c3:
        flight_only = st.toggle(
            "Flight experiments only",
            value=True,
            key="lib_flight",
            help="Hide the five ground/modelling studies.",
        )
        focus_on = st.toggle(
            "Filter by sidebar materials",
            value=False,
            key="lib_materials",
            help="Filter to records that mention the material classes selected in the sidebar.",
        )

    view = filter_records(
        df,
        pillar=pillar,
        program=program,
        flight_only=flight_only,
        query=query,
        materials=st.session_state.get("materials", []),
        focus_materials=focus_on,
    )

    active = []
    if pillar != "All":
        active.append(pillar)
    if program != "All":
        active.append(program)
    if flight_only:
        active.append("flight only")
    if focus_on:
        focus = st.session_state.get("materials", [])
        active.append("materials: " + (", ".join(focus) if focus else "none selected"))
    if query.strip():
        active.append(f"search: “{query.strip()}”")

    stats_col, action_col = st.columns([3, 1])
    with stats_col:
        st.caption(
            f"Showing **{len(view)} of {len(df)}** records · "
            f"{int(view['is_core'].sum())} core · "
            f"{int((view['gravity'] == 'microgravity').sum())} flight"
            + (f" · filters: {'; '.join(active)}" if active else " · no filters applied")
        )
    with action_col:
        if active:
            st.button("Clear filters", on_click=_clear_filters, width="stretch")

    if focus_on and not st.session_state.get("materials"):
        st.info("Choose at least one material class in the sidebar to use the material filter.")

    export_cols = [
        "psi_id",
        "short_name",
        "name",
        "fire_safety_phase",
        "gravity",
        "program",
        "facility",
        "year_start",
        "year_end",
        "materials",
        "objective",
        "key_finding",
        "safety_implication",
        "limitations",
        "confidence",
        "psi_url",
    ]
    st.download_button(
        "Download this view (CSV)",
        view[export_cols].to_csv(index=False).encode("utf-8"),
        "flame-in-freefall-records.csv",
        "text/csv",
        help="Filtered PSI metadata with links back to each record. Numeric conditions are in Compare.",
    )

    if view.empty:
        st.warning(
            "No investigations match these filters. Try a broader pillar, clear the search, "
            "or turn off the material filter."
        )
        st.button("Clear all filters", on_click=_clear_filters)
        return

    rows = view.to_dict("records")
    for i in range(0, len(rows), 2):
        left, right = st.columns(2, gap="medium")
        with left:
            _card(rows[i], selected)
        if i + 1 < len(rows):
            with right:
                _card(rows[i + 1], selected)
