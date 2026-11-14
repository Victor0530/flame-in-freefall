"""Visual theme for the dashboard."""

import streamlit as st

CSS = """
<style>
:root {
  --bg: #080c18;
  --panel: #11182b;
  --panel-2: #0d1322;
  --line: #24304d;
  --text: #e8ecf7;
  --muted: #98a3bd;
  --accent: #ff7a3d;
  --accent-2: #ffc46b;
}
.stApp { background: radial-gradient(1200px 600px at 15% -10%, #17203a 0%, #080c18 55%) fixed; }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1250px; }
h1, h2, h3, h4 { color: var(--text); letter-spacing: -0.01em; }
p, li, label, span { color: var(--text); }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b1120 0%, #0a0f1c 100%);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }
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
.kpi .l { font-size: 0.78rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }
.card {
  border: 1px solid var(--line); background: var(--panel);
  border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;
}
.card h4 { margin: 6px 0 4px 0; font-size: 1.05rem; }
.card .full { color: var(--muted); font-size: 0.8rem; margin-bottom: 10px; }
.card .meta { color: var(--muted); font-size: 0.8rem; margin-bottom: 10px; }
.card .lab { color: var(--accent-2); font-size: 0.7rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; }
.card .body { font-size: 0.88rem; color: #cdd5e8; margin: 2px 0 10px 0; }
.rule { border-left: 3px solid var(--accent); padding-left: 12px; margin: 10px 0; }
.note { color: var(--muted); font-size: 0.78rem; }
.pill {
  display:inline-block; padding:3px 10px; border-radius:999px; font-size:.72rem;
  border:1px solid var(--line); color:var(--muted); margin-right:6px;
}
div[data-testid="stMetric"] {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 14px; padding: 12px 14px;
}
.stButton > button, .stLinkButton > a {
  border-radius: 10px; border: 1px solid var(--line);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(90deg, #ff7a3d, #ff9f5a); border: none; color: #12100d;
  font-weight: 700;
}
code { color: #ffc46b; }
</style>
"""


def apply() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )
