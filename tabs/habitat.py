"""Habitat Checker tab: ppO2, historical envelope, risk framing."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from lib.data import (
    EXPLORATION_PPO2_KPA,
    PRESETS,
    STD_O2_PCT,
    STD_PPO2_KPA,
    STD_PRESSURE_KPA,
    load_investigations,
    phase_meta,
)


def _gauge(ppo2: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=ppo2,
            number={"suffix": " kPa", "font": {"size": 42, "color": "#e8ecf7"}},
            title={"text": "Oxygen partial pressure", "font": {"size": 14, "color": "#98a3bd"}},
            gauge={
                "axis": {"range": [0, 40], "tickcolor": "#5a6580", "tickfont": {"color": "#98a3bd"}},
                "bar": {"color": "#ff7a3d", "thickness": 0.28},
                "bgcolor": "#0d1322",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 16], "color": "#16324a"},
                    {"range": [16, 21.1], "color": "#1d4a3a"},
                    {"range": [21.1, 40], "color": "#4a2020"},
                ],
                "threshold": {
                    "line": {"color": "#ffc46b", "width": 3},
                    "thickness": 0.8,
                    "value": STD_PPO2_KPA,
                },
            },
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=24, r=24, t=48, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e8ecf7"},
    )
    return fig


def render() -> None:
    st.markdown("### Habitat Checker")
    st.caption(
        "Set a cabin atmosphere and compare it with the historical NASA-STD-6001B Test 1 point "
        "and the current exploration atmosphere. Framing only â€” not a certification tool."
    )

    preset = st.selectbox("Start from a preset", list(PRESETS.keys()), index=2)
    default_o2, default_p = PRESETS[preset]
    if st.session_state.get("_preset") != preset:
        st.session_state["o2_pct"] = float(default_o2)
        st.session_state["pressure_kpa"] = float(default_p)
        st.session_state["_preset"] = preset

    c1, c2 = st.columns(2)
    with c1:
        o2 = st.slider("Oxygen concentration (%)", 10.0, 100.0, step=0.5, key="o2_pct")
    with c2:
        pressure = st.slider("Total pressure (kPa)", 20.0, 101.4, step=0.1, key="pressure_kpa")

    ppo2 = o2 / 100 * pressure
    above_o2 = o2 > STD_O2_PCT
    above_ppo2 = ppo2 > STD_PPO2_KPA

    st.plotly_chart(_gauge(ppo2), width="stretch", config={"displayModeBar": False})

    m1, m2, m3 = st.columns(3)
    m1.metric("ppOâ‚‚", f"{ppo2:.1f} kPa")
    m2.metric("Historical Test 1 max", f"{STD_O2_PCT:.0f}% @ {STD_PRESSURE_KPA:.1f} kPa", f"{STD_PPO2_KPA:.1f} kPa ppOâ‚‚")
    m3.metric("Exploration atmosphere", "34% @ 56.5 kPa", f"{EXPLORATION_PPO2_KPA:.1f} kPa ppOâ‚‚")

    if above_o2 and above_ppo2:
        st.error(
            f"**Above the historical Test 1 point.** This atmosphere is {o2:.1f}% Oâ‚‚ at {pressure:.1f} kPa "
            f"({ppo2:.1f} kPa ppOâ‚‚). It exceeds both the 30% Oâ‚‚ concentration and the {STD_PPO2_KPA:.1f} kPa "
            "ppOâ‚‚ of the NASA-STD-6001B Test 1 envelope."
        )
    elif above_o2 or above_ppo2:
        st.warning(
            f"**Mixed result.** {'Oxygen concentration' if above_o2 else 'ppOâ‚‚'} exceeds the historical "
            "Test 1 point while the other does not. Treat the configuration as needing low-gravity evidence."
        )
    else:
        st.success(
            "Below the historical Test 1 point on both axes. That is necessary, not sufficient: "
            "Test 1 is a 1-g upward-propagation test and is not conservative for low-gravity fires."
        )

    st.markdown(
        f"""
        <div class="rule">
        <b>Why the historical point matters.</b> NASA-STD-6001B Test 1 screened materials at up to
        {STD_O2_PCT:.0f}% Oâ‚‚ and {STD_PRESSURE_KPA:.1f} kPa ({STD_PPO2_KPA:.1f} kPa ppOâ‚‚) using 1-g upward
        flame propagation. Microgravity removes buoyant flow, so a material that passes at 1-g can still
        burn in orbit. The current exploration atmosphere (34% Oâ‚‚ / 56.5 kPa) sits at
        {EXPLORATION_PPO2_KPA:.1f} kPa ppOâ‚‚ â€” a higher Oâ‚‚ fraction than Test 1, at lower total pressure.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### What the evidence says")
    df = load_investigations()
    df = df[(df["gravity"] == "microgravity")].copy()
    picks = []
    for pid in ["saffire-ii", "bass-ii", "acme-cfi-g", "same"]:
        hit = df[df["id"] == pid]
        if not hit.empty:
            picks.append(hit.iloc[0])

    if not picks:
        st.info("Investigation library not found.")
        return

    for row in picks:
        meta = phase_meta(row["fire_safety_phase"])
        with st.expander(f"{meta['icon']} {row['short_name']} â€” {row['key_finding']}"):
            st.markdown(f"**Safety implication.** {row['safety_implication']}")
            st.markdown(f"**Limitation.** {row['limitations']}")
            st.caption(f"{row['psi_id']} Â· {row['facility']}")

    st.markdown("#### Design rules this view implies")
    st.markdown(
        """
- **Do not treat a 1-g pass as low-g clearance.** Require microgravity or partial-gravity evidence for
  materials used above the Test 1 oxygen concentration.
- **Ventilation changes the answer.** Saffire-III and BASS-II show flow speed alters spread and extinction;
  design rules should state the flow condition they assume.
- **Detection is material-dependent.** SAME and SAME-R measured low-g smoke particle sizes that differ from
  terrestrial smoke; detector selection should follow the materials actually present.
- **Suppression margins need low-g data.** FLEX/FLEX-2 show inert-gas dilution works, but the limiting oxygen
  index must be measured, not inferred from 1-g.
        """
    )
    st.caption(
        "Caveat: no PSI experiment tested this exact Oâ‚‚/pressure combination, and no partial-gravity combustion "
        "dataset exists at habitat scale. This is decision support, not a flammability certification."
    )
