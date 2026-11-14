"""Flame in Freefall â€” SI-powered fire safety insights from microgravity combustion data."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Flame in Freefall",
    page_icon="ðŸ”¥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from lib import theme  # noqa: E402
from lib.data import (  # noqa: E402
    CORE_IDS,
    PRESETS,
    badge,
    evidence_counts,
    load_investigations,
    phase_meta,
)
from tabs import advisor, compare, habitat, library  # noqa: E402

theme.apply()

DESTINATIONS = {
    "Moon habitat": (34.0, 56.5, "34% Oâ‚‚ / 8.2 psia exploration atmosphere"),
    "Mars transit": (34.0, 56.5, "34% Oâ‚‚ / 8.2 psia exploration atmosphere"),
    "ISS (current)": (21.0, 101.3, "21% Oâ‚‚ / 14.7 psia cabin air"),
    "EMU spacesuit": (100.0, 29.6, "100% Oâ‚‚ / 4.3 psia"),
}

st.session_state.setdefault("selected", [])

df = load_investigations()
counts = evidence_counts(df)

with st.sidebar:
    st.markdown(
        '<div style="font-size:1.35rem;font-weight:800;letter-spacing:-.01em;">ðŸ”¥ Flame in Freefall</div>'
        '<div class="note" style="margin-bottom:14px;">Microgravity combustion â†’ habitat fire safety</div>',
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
        help="Used to prioritise evidence once numeric test conditions are curated.",
    )

    if st.button("Apply atmosphere to Habitat Checker", width="stretch"):
        st.session_state["o2_pct"] = float(o2_default)
        st.session_state["pressure_kpa"] = float(p_default)
        st.toast("Habitat Checker updated")

    ppo2 = o2_default / 100 * p_default
    st.markdown(
        f'<div class="kpi"><div class="n">{ppo2:.1f} kPa</div>'
        f'<div class="l">ppOâ‚‚ Â· {o2_default:.0f}% at {p_default:.1f} kPa</div></div>',
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
    st.caption(
        f"PSI metadata: **{counts['total']} records** ({counts['flight']} flight)\n\n"
        f"Core investigations: **{counts['core']}/{len(CORE_IDS)}**\n\n"
        f"Hand-reviewed: **{counts['reviewed']}/{counts['total']}**"
    )
    st.caption(
        "Source: NASA Physical Sciences Informatics. Decision support only â€” "
        "not a flammability certification."
    )

st.markdown(
    """
    <div class="hero">
      <h1>Flame in Freefall</h1>
      <p>NASA's microgravity combustion experiments, turned into evidence-ranked fire-safety decisions for
      Moon and Mars habitats â€” with a citation behind every claim, and an explicit answer when the data
      does not exist.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

k = st.columns(4)
for col, (value, label) in zip(
    k,
    [
        (counts["total"], "PSI investigations"),
        (counts["flight"], "Flight experiments"),
        (counts["core"], "Core deep-curated"),
        (len(PRESETS), "Atmosphere presets"),
    ],
):
    with col:
        st.markdown(
            f'<div class="kpi"><div class="n">{value}</div><div class="l">{label}</div></div>',
            unsafe_allow_html=True,
        )

st.write("")

tab_library, tab_compare, tab_habitat, tab_advisor = st.tabs(
    ["ðŸ“š Experiment Library", "âš–ï¸ Compare & Rank", "ðŸ›¡ï¸ Habitat Checker", "ðŸ’¬ Evidence Advisor"]
)

with tab_library:
    library.render()

with tab_compare:
    compare.render()

with tab_habitat:
    habitat.render()

with tab_advisor:
    advisor.render()
