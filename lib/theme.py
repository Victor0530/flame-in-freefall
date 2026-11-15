"""Visual theme for the dashboard."""

import streamlit as st

CSS = """
<style>
:root {
  --bg: #080c18;
  --panel: #11182b;
  --panel-2: #0d1322;
  --line: #24304d;
  --line-strong: #34436a;
  --text: #e8ecf7;
  --muted: #a7b1c8;
  --accent: #ff7a3d;
  --accent-2: #ffc46b;
  --good: #7ee787;
  --warn: #ffc46b;
  --bad: #ff8d8d;
  --info: #7cc7ff;
}
.stApp { background: radial-gradient(1200px 600px at 15% -10%, #17203a 0%, #080c18 55%) fixed; }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1250px; }
h1, h2, h3, h4 { color: var(--text); letter-spacing: -0.01em; }
p, li, label, span { color: var(--text); }
a { color: var(--accent-2); text-underline-offset: 2px; }
a:hover { color: #ffe0a3; }
::selection { background: #ff7a3d55; }
:focus-visible { outline: 2px solid var(--accent-2); outline-offset: 2px; border-radius: 4px; }

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b1120 0%, #0a0f1c 100%);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }
[data-testid="stSidebar"] h2 { font-size: 0.98rem; margin: 0.2rem 0 0.45rem 0; }

.hero {
  border: 1px solid var(--line);
  background: linear-gradient(120deg, #141c33 0%, #0d1322 60%);
  border-radius: 18px;
  padding: 22px 26px;
  margin-bottom: 18px;
  position: relative;
  overflow: hidden;
}
.hero:after {
  content: "";
  position: absolute; right: -60px; top: -80px; width: 260px; height: 260px;
  background: radial-gradient(circle, #ff7a3d33 0%, transparent 70%);
}
.hero h1 { margin: 0 0 6px 0; font-size: 2.05rem; }
.hero p { margin: 0; color: var(--muted); max-width: 780px; }

.kpi {
  border: 1px solid var(--line); background: var(--panel);
  border-radius: 14px; padding: 14px 16px; height: 100%;
}
.kpi .n { font-size: 1.65rem; font-weight: 700; color: var(--text); line-height: 1.1; }
.kpi .l { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.kpi .note { margin-top: 4px; }

.card {
  border: 1px solid var(--line); background: var(--panel);
  border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;
}
.card h3, .card h4 { margin: 6px 0 4px 0; font-size: 1.05rem; }
.card .full { color: var(--muted); font-size: 0.8rem; margin-bottom: 10px; }
.card .meta { color: var(--muted); font-size: 0.8rem; margin-bottom: 10px; }
.card .lab { color: var(--accent-2); font-size: 0.7rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; }
.card .body { font-size: 0.9rem; line-height: 1.5; color: #d7deee; margin: 2px 0 10px 0; }
.card.compact { padding: 13px 15px; }
.card.compact h4 { font-size: 1rem; }

.rule { border-left: 3px solid var(--accent); padding-left: 12px; margin: 10px 0; }
.note { color: var(--muted); font-size: 0.8rem; line-height: 1.45; }
.pill {
  display:inline-block; padding:3px 10px; border-radius:999px; font-size:.72rem;
  border:1px solid var(--line-strong); color:var(--muted); margin: 0 6px 4px 0;
}
.status {
  display:inline-flex; align-items:center; gap:6px; padding:4px 10px; border-radius:999px;
  font-size:0.78rem; font-weight:600; border:1px solid currentColor;
}
.status.good { color: var(--good); background: #7ee78715; }
.status.warn { color: var(--warn); background: #ffc46b15; }
.status.bad { color: var(--bad); background: #ff8d8d15; }
.status.info { color: var(--info); background: #7cc7ff15; }

div[data-testid="stMetric"] {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 14px; padding: 12px 14px;
}
.stButton > button, .stLinkButton > a, .stDownloadButton > button {
  border-radius: 10px; border: 1px solid var(--line);
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
  background: linear-gradient(90deg, #ff7a3d, #ff9f5a); border: none; color: #12100d;
  font-weight: 700;
}
.stButton > button:disabled { opacity: 0.55; }

/* Selected multiselect tags: the default white-on-orange pair fails WCAG AA. */
span[data-baseweb="tag"] {
  background-color: #ff7a3d !important;
  color: #12100d !important;
  border: 1px solid #ffc46b !important;
}
span[data-baseweb="tag"] span { color: #12100d !important; }
span[data-baseweb="tag"] svg { fill: #12100d !important; }

code { color: #ffc46b; }

@media (max-width: 700px) {
  .block-container { padding-top: 1.2rem; padding-left: 1rem; padding-right: 1rem; }
  .hero { padding: 18px 18px; }
  .hero h1 { font-size: 1.6rem; }
  .card { padding: 14px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>
"""


def apply() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )
