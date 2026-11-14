"""Flame in Freefall — SI-powered fire safety insights from microgravity combustion data."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Flame in Freefall",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from lib import theme  # noqa: E402
from lib.data import (  # noqa: E402
    CORE_IDS,
    badge,
    evidence_counts,
    load_conditions,
    load_faq,
    load_investigations,
    phase_meta,
)
from tabs import advisor, compare, habitat, library  # noqa: E402

theme.apply()

DESTINATIONS = {
    "Moon habitat": (34.0, 56.5, "34% O₂ / 8.2 psia exploration atmosphere"),
    "Mars transit": (34.0, 56.5, "34% O₂ / 8.2 psia exploration atmosphere"),
    "ISS (current)": (21.0, 101.3, "21% O₂ / 14.7 psia cabin air"),
    "EMU spacesuit": (100.0, 29.6, "100% O₂ / 4.3 psia"),
}

st.session_state.setdefault("selected", [])

df = load_investigations()
counts = evidence_counts(df)

with st.sidebar:
    st.markdown(
        '<div style="font-size:1.12rem;font-weight:800;letter-spacing:-.01em;white-space:nowrap;">🔥 Flame in Freefall</div>'
        '<div class="note" style="margin-bottom:14px;">Microgravity fire safety, evidence-first</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Mission context")
    destination = st.selectbox("Destination", list(DESTINATIONS.keys()), index=0)
    o2_default, p_default, atmosphere = DESTINATIONS[destination]
    st.caption(atmosphere)

    materials = st.multiselect(
        "Material focus",
        ["Fabrics", "Plastics", "Electronics", "Paper / packaging", "Liquids / fuels"],
        default=["Fabrics", "Plastics"],
        key="materials",
        help="Filters the library to records whose material description mentions the selected classes.",
    )

    if st.button("Apply atmosphere to Habitat Checker", width="stretch"):
        st.session_state["o2_pct"] = float(o2_default)
        st.session_state["pressure_kpa"] = float(p_default)
        st.toast("Habitat Checker updated")

    ppo2 = o2_default / 100 * p_default
    st.markdown(
        f'<div class="kpi"><div class="n">{ppo2:.1f} kPa</div>'
        f'<div class="l">Oxygen partial pressure</div>'
        f'<div class="note">{o2_default:.0f}% at {p_default:.1f} kPa</div></div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("#### Comparison tray")
    selected = st.session_state["selected"]
    if selected:
        names = df[df["id"].isin(selected)]["short_name"].tolist()
        st.markdown("".join(f'<span class="pill">{n}</span>' for n in names), unsafe_allow_html=True)
        if st.button("Clear selection", width="stretch"):
            st.session_state["selected"] = []
            st.rerun()
        st.caption("Open **Compare & Rank** to review them side by side.")
    else:
        st.caption("Add investigations from the library (up to 4).")

    st.divider()
    st.markdown("#### Data status")
    cond = load_conditions()
    documented = cond[cond["point_type"].isin(["specific", "range"])]["investigation_id"].nunique()
    faq_count = len(load_faq())
    st.caption(
        f"PSI metadata: **{counts['total']} records** ({counts['flight']} flight)\n\n"
        f"Core investigations: **{counts['core']}/{len(CORE_IDS)}**\n\n"
        f"With numeric conditions: **{documented}**\n\n"
        f"Reviewed Q&A: **{faq_count}**"
    )
    st.caption(
        "Source: NASA Physical Sciences Informatics. Decision support only — "
        "not a flammability certification."
    )

st.markdown(
    """
    <div class="hero">
      <h1>Flame in Freefall</h1>
      <p>NASA's microgravity combustion experiments, turned into evidence-ranked fire-safety decisions for
      Moon and Mars habitats — with a citation behind every claim, and an explicit answer when the data
      does not exist.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

k = st.columns(4)
for col, (value, label) in zip(
    k,
    [
        (counts["total"], "Records"),
        (counts["flight"], "Flight"),
        (counts["core"], "Core"),
        (3, "Pillars"),
    ],
):
    with col:
        st.markdown(
            f'<div class="kpi"><div class="n">{value}</div><div class="l">{label}</div></div>',
            unsafe_allow_html=True,
        )

st.write("")

tab_library, tab_compare, tab_habitat, tab_advisor = st.tabs(
    ["📚 Library", "⚖️ Compare", "🛡️ Habitat Checker", "💬 Advisor"]
)

with tab_library:
    library.render()

with tab_compare:
    compare.render()

with tab_habitat:
    habitat.render()

with tab_advisor:
    advisor.render()

st.divider()
foot1, foot2, foot3 = st.columns(3)
with foot1:
    st.markdown("##### Data")
    st.caption(
        f"{counts['total']} PSI investigations ({counts['flight']} flight, {len(CORE_IDS)} core), "
        "NASA-STD-6001B and JSC 29353 for requirements, NTRS abstracts and the 2015 "
        "Researcher's Guide for context."
    )
with foot2:
    st.markdown("##### Method")
    st.caption(
        "Conditions are quoted from source text, never inferred. Ranking drops missing dimensions "
        "and reports coverage. Advisor answers are reviewed or grounded in retrieved passages."
    )
with foot3:
    st.markdown("##### Limits")
    st.caption(
        "Decision support, not flight certification. Public PSI records omit numeric conditions for "
        "most experiments, and 1-g screening does not bound microgravity behaviour."
    )
st.caption(
    "Built for NASA Space Apps Challenge 2026 · "
    "[github.com/Victor0530/flame-in-freefall](https://github.com/Victor0530/flame-in-freefall) · "
    "Data © NASA, used under NASA media guidelines."
)

