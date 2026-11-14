"""Evidence Advisor tab."""

from __future__ import annotations

import html

import streamlit as st

from lib.advisor import ask, retrieve
from lib.data import badge

QUESTIONS = [
    "Which experiments tested flammability at high oxygen concentration?",
    "What do we know about smoke detection in microgravity?",
    "How is a microgravity fire suppressed?",
    "What should a Moon habitat test first?",
    "How does the 34% oxygen atmosphere compare with NASA-STD-6001 Test 1?",
    "Why is 1-g material screening not sufficient for spacecraft?",
]

MODE_STYLE = {
    "reviewed": ("Reviewed answer", "#7ee787"),
    "gemini": ("Gemini-grounded", "#4cc9f0"),
    "cached": ("Cached answer", "#8b93a7"),
    "offline": ("Offline extractive", "#ff8a3d"),
    "empty": ("No match", "#ff5c5c"),
}


def _run(question: str, use_llm: bool) -> None:
    with st.spinner("Retrieving passages and checking sources…"):
        st.session_state["advisor_result"] = ask(question, allow_generation=use_llm)
        st.session_state["advisor_question"] = question


def _render_result(use_llm: bool) -> None:
    result = st.session_state.get("advisor_result")
    if not result:
        return
    question = st.session_state.get("advisor_question", "")
    label, colour = MODE_STYLE.get(result["mode"], ("Answer", "#8b93a7"))

    st.markdown(f"**Q:** {html.escape(question)}")
    tags = badge(label, colour)
    if result["cached"]:
        tags += badge("served from cache", "#8b93a7")
    st.markdown(tags, unsafe_allow_html=True)
    st.markdown(
        f'<div class="rule"><div class="body">{html.escape(result["answer"]).replace(chr(10), "<br>")}</div></div>',
        unsafe_allow_html=True,
    )

    if result["sources"]:
        st.markdown("###### Sources used")
        for src in result["sources"]:
            st.markdown(
                f"- **[{src['tag']}]** [{html.escape(src['label'])}]({src['url']}) — "
                f"{html.escape(src['locator'])}"
            )
    st.caption(
        "Citations are the retrieved passages only. No source is listed that the retrieval step did not return."
    )


def render() -> None:
    st.markdown("### Evidence Advisor")
    st.caption(
        "Retrieval-augmented answers over PSI records, NASA standards and NTRS abstracts — "
        "every claim carries a passage tag, and the passages are shown below the answer."
    )

    use_llm = st.toggle("Use Gemini to compose the answer", value=True)
    if not use_llm:
        st.caption("Generation is off: answers are quoted directly from retrieved NASA text.")

    with st.form("advisor_form", clear_on_submit=False):
        question = st.text_input(
            "Ask about microgravity fire safety",
            placeholder="e.g. Which experiments constrain material flammability at 34% oxygen?",
        )
        submitted = st.form_submit_button("Ask the evidence base")

    if submitted and question.strip():
        _run(question.strip(), use_llm)

    st.markdown("**Suggested questions**")
    for i, q in enumerate(QUESTIONS):
        if st.button(q, key=f"q_{i}", width="stretch"):
            _run(q, use_llm)

    _render_result(use_llm)

    passages = retrieve(st.session_state.get("advisor_question", ""), k=4) if st.session_state.get("advisor_result") else []
    if passages:
        with st.expander("Retrieved passages", expanded=False):
            for p in passages:
                st.markdown(f"**[{p['tag']}]** {html.escape(p['source_label'])} · score {p['score']:.2f}")
                st.caption(p["text"][:420] + ("…" if len(p["text"]) > 420 else ""))

    st.warning(
        "AI-assisted content, grounded in retrieved NASA text. Human review is required before any "
        "claim is used in a design decision; the advisor reports evidence, not approvals."
    )
