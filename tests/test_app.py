"""End-to-end smoke test for all four Streamlit tabs.

AppTest executes the real app script, so this catches runtime API changes that
unit tests miss (widget arguments, missing state, broken column config).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def app() -> AppTest:
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=180).run()


def test_app_renders_all_tabs_without_exceptions(app: AppTest) -> None:
    assert not app.exception, [e.value for e in app.exception]
    assert len(app.tabs) == 4
    assert [tab.label for tab in app.tabs][0].endswith("Library")
    assert [tab.label for tab in app.tabs][3].endswith("Advisor")


def test_advisor_starts_with_guidance(app: AppTest) -> None:
    messages = " ".join(str(item.value) for item in app.info)
    assert "Ask about a specific experiment" in messages


def test_library_search_and_clear_filters(app: AppTest) -> None:
    app.text_input(key="lib_query").set_value("soot").run()
    assert not app.exception
    assert app.text_input(key="lib_query").value == "soot"

    clear = [button for button in app.button if button.label == "Clear filters"]
    assert clear, "an active filter should offer a clear action"
    clear[0].click().run()
    assert not app.exception
    assert app.toggle(key="lib_flight").value is False
    assert app.text_input(key="lib_query").value == ""


def test_habitat_accepts_pressure_above_old_gauge_range(app: AppTest) -> None:
    app.slider(key="o2_pct").set_value(100.0)
    app.slider(key="pressure_kpa").set_value(101.4)
    app.run()
    assert not app.exception
    assert app.slider(key="o2_pct").value == 100.0
    assert app.slider(key="pressure_kpa").value == 101.4


def test_compare_weight_preset_runs(app: AppTest) -> None:
    preset = [button for button in app.button if button.label == "Atmosphere first"]
    assert preset, "weight presets should be available"
    preset[0].click().run()
    assert not app.exception
