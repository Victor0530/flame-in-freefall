"""Evidence Advisor tab."""

from __future__ import annotations

import streamlit as st


QUESTIONS = [
    "Which experiments tested flammability at high oxygen concentration?",
    "What do we know about smoke detection in microgravity?",
    "How is a microgravity fire suppressed?",
    "What should a Moon habitat test first?",
]


def render() -> None:
    st.markdown("### Evidence Advisor")
    st.caption(
        "Retrieval-augmented answers over PSI metadata, NASA standards and NTRS abstracts â€” "
        "every sentence traceable to a source."
    )

    st.text_input(
        "Ask about microgravity fire safety",
        placeholder="e.g. Which experiments constrain material flammability at 34% oxygen?",
        disabled=True,
        help="Enabled once the corpus and cache are built.",
    )
    st.markdown("**Suggested questions**")
    for q in QUESTIONS:
        st.button(q, disabled=True, width="stretch", key=f"q_{q[:20]}")

    st.info(
        "The advisor is wired to Gemini 3.5 Flash-Lite with TF-IDF retrieval, a cached answer set and an "
        "extractive offline fallback. It is intentionally disabled until the corpus is built and reviewed â€” "
        "an uncited answer would undercut the project's main claim."
    )

    with st.expander("Planned answer contract"):
        st.markdown(
            """
Every generated answer must return structured JSON with:

- **answer** â€” two to four sentences, no numbers without a citation.
- **key_points** â€” three bullets.
- **citations** â€” source id, locator and URL.
- **confidence** â€” high / medium / low.
- **caveats** â€” especially the partial-gravity gap.

If the model is unavailable (no key, quota, offline), the app serves a cached or extractive answer and
labels it as such. AI-assisted content is marked and human-reviewed before the demo.
            """
        )
