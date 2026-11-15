"""Evidence Advisor tab."""

from __future__ import annotations

import html

import streamlit as st

from lib.advisor import MAX_QUESTION_CHARS, api_key_available, ask
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
    "reviewed": ("Human-reviewed answer", "#7ee787"),
    "gemini": ("Gemini-grounded", "#4cc9f0"),
    "cached": ("Cached answer", "#8b93a7"),
    "offline": ("Offline extractive", "#ff8a3d"),
    "empty": ("No match", "#ff5c5c"),
}


def _run(question: str, use_llm: bool) -> None:
    with st.spinner("Retrieving passages, checking citations and composing an answer…"):
        st.session_state["advisor_result"] = ask(question, allow_generation=use_llm)
        st.session_state["advisor_question"] = question


def _citation_badge(audit: dict) -> str:
    status = audit.get("status")
    if status == "ok":
        return badge("✓ Citations checked", "#7ee787")
    if status == "reviewed":
        return badge("✓ Reviewed sources", "#7ee787")
    if status == "unsupported":
        unknown = ", ".join(audit.get("unknown", []))
        return badge(f"⚠ Unsupported citation: {unknown}", "#ff8a3d")
    if status == "missing":
        return badge("⚠ No citation tags in answer", "#ffc46b")
    return ""


def _render_result() -> None:
    result = st.session_state.get("advisor_result")
    if not result:
        return

    question = st.session_state.get("advisor_question", "")
    label, colour = MODE_STYLE.get(result["mode"], ("Answer", "#8b93a7"))
    audit = result.get("citations") or {}

    st.markdown("### Answer")
    st.markdown(f"**Q:** {html.escape(question)}")
    tags = badge(label, colour)
    if result.get("cached"):
        tags += badge("served from cache", "#8b93a7")
    tags += _citation_badge(audit)
    st.markdown(tags, unsafe_allow_html=True)
    st.markdown(
        f'<div class="rule"><div class="body">{html.escape(result["answer"]).replace(chr(10), "<br>")}</div></div>',
        unsafe_allow_html=True,
    )

    sources = result.get("sources") or []
    if sources:
        st.markdown("#### Sources")
        for src in sources:
            url = str(src.get("url") or "")
            lab = html.escape(str(src.get("label") or "Untitled source"))
            locator = html.escape(str(src.get("locator") or "locator not stated"))
            if url.startswith(("http://", "https://")):
                st.markdown(f"- **[{html.escape(str(src['tag']))}]** [{lab}]({url}) — {locator}")
            else:
                st.markdown(f"- **[{html.escape(str(src['tag']))}]** {lab} — {locator}")
        if audit.get("cited"):
            st.caption("Only the passages cited in the answer are listed.")
        else:
            st.caption(
                "No passage tags were found in the answer, so every retrieved passage is listed "
                "for verification rather than claiming a citation that is not there."
            )
    elif result["mode"] != "empty":
        st.warning("This answer has no sources attached. Treat it as unverified.")

    retrieved = result.get("retrieved") or []
    if retrieved:
        with st.expander(f"Retrieved passages ({len(retrieved)})", expanded=False):
            for p in retrieved:
                scores = p.get("scores") or {}
                detail = f"fused {p.get('score', 0):.2f}"
                if scores:
                    detail += f" · semantic {scores.get('semantic', 0):.2f} · keyword {scores.get('keyword', 0):.2f}"
                st.markdown(
                    f"**[{p['tag']}]** {html.escape(p.get('source_label', 'Untitled'))} · "
                    f"{html.escape(detail)} · {p.get('method', 'retrieval')}"
                )
                text = p.get("text", "")
                st.caption(text[:500] + ("…" if len(text) > 500 else ""))

    if st.button("Clear answer", key="clear_advisor"):
        st.session_state.pop("advisor_result", None)
        st.session_state.pop("advisor_question", None)
        st.rerun()


def render() -> None:
    st.markdown("## Evidence Advisor")
    st.caption(
        "Retrieval-augmented answers over PSI records, NASA standards and NTRS abstracts — "
        "every cited claim carries a passage tag, and the retrieved passages stay visible for checking."
    )

    has_key = api_key_available()
    use_llm = st.toggle(
        "Compose with Gemini when a key is configured",
        value=has_key,
        key="advisor_use_llm",
        help="When off, the answer quotes retrieved NASA sentences directly instead of calling a model.",
    )
    if has_key and use_llm:
        st.caption("Gemini key detected. If generation fails, the answer falls back to quoted passages.")
    elif not has_key:
        st.caption("No Gemini key configured: answers are quoted directly from retrieved NASA text.")
    else:
        st.caption("Generation is off: answers are quoted directly from retrieved NASA text.")

    if not st.session_state.get("advisor_result"):
        st.info(
            "Ask about a specific experiment, material, atmosphere, or fire-safety phase. "
            "If the evidence base does not cover it, the advisor says so instead of guessing."
        )

    with st.form("advisor_form", clear_on_submit=False):
        question = st.text_input(
            "Ask about microgravity fire safety",
            placeholder="e.g. Which experiments constrain material flammability at 34% oxygen?",
            max_chars=MAX_QUESTION_CHARS,
            key="advisor_question_input",
        )
        submitted = st.form_submit_button("Ask the evidence base", type="primary")

    if submitted:
        if question.strip():
            _run(question.strip(), use_llm)
        else:
            st.warning("Enter a question, or choose one of the suggested questions below.")

    st.markdown("### Suggested questions")
    for i, q in enumerate(QUESTIONS):
        if st.button(q, key=f"q_{i}", width="stretch"):
            _run(q, use_llm)

    _render_result()

    st.warning(
        "AI-assisted content, grounded in retrieved NASA text. Human review is required before any "
        "claim is used in a design decision; the advisor reports evidence, not approvals."
    )
