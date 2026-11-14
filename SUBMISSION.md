# SUBMISSION — Flame in Freefall

> **Event:** NASA Space Apps Challenge 2026 (global window Sat 14 Nov 09:00 – Sun 15 Nov 23:59 local)
> **Repo:** https://github.com/Victor0530/flame-in-freefall
> **Video:** _[paste unlisted YouTube link]_
> **App:** _[paste Streamlit Cloud URL once deployed]_
>
> Submit by 20:00 local, then keep the rest of the evening as buffer.

---

## 1. Checklist

### Project page

- [x] Project title — Flame in Freefall
- [x] Tagline
- [x] Challenge selected — Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data
- [x] Team members — solo (Victor Yang)
- [x] Short description
- [x] How it works
- [x] Data and sources
- [x] Technical approach
- [x] Limitations and caveats
- [x] What is next
- [x] Built with
- [x] Credits
- [x] Repo URL
- [ ] Demo URL (Streamlit Cloud, after deploy)
- [ ] Video URL
- [x] Screenshots (`docs/screenshots/`)

### Repository

- [x] Public and judge-accessible
- [x] `README.md` complete
- [x] `requirements.txt` pinned
- [x] `.gitignore` excludes `.venv/`, `.env`, `.streamlit/secrets.toml`
- [x] No API keys committed (`git ls-files` checked)
- [ ] Fresh clone verified on a clean machine (local venv verified)
- [x] Data files and sources included
- [x] License and credits (MIT)
- [x] Commit history starts inside the event window

### Demo

- [x] Local app runs
- [ ] Streamlit Cloud app runs
- [x] Offline mode works (extractive fallback, reviewed answers)
- [ ] 90-second live demo rehearsed
- [ ] 2-minute video recorded and uploaded
- [ ] Backup video saved

### Final checks

- [x] Every number has a source locator
- [x] Units consistent (%, kPa, cm/s, ppO₂)
- [x] NASA-STD-6001 and >30% O₂ statement checked
- [x] Partial-gravity caveat present
- [x] Prototype disclaimer present
- [x] AI assistance disclosed
- [x] No NASA endorsement implied
- [ ] All links tested from a logged-out browser
- [ ] Submission completed before the deadline

---

## 2. Project page copy

### Title

**Flame in Freefall — Evidence-ranked fire safety for Moon and Mars habitats**

### Tagline

NASA's microgravity combustion data, turned into cited, evidence-ranked fire-safety decisions — with an explicit answer when the data does not exist.

### Short description

Flame in Freefall is a Streamlit dashboard that makes NASA's Physical Sciences Informatics (PSI) combustion collection usable for habitat fire-safety decisions. It covers all 24 public combustion investigations, ranks them against a chosen cabin atmosphere with a transparent score, checks oxygen partial pressure against NASA-STD-6001B envelopes, and answers fire-safety questions with passage-level citations. Where NASA has not published a condition, the app shows the gap instead of guessing.

### How it works

1. **Ingest** — PSI JSON API gives all 24 investigations (19 flight, 5 ground); NTRS gives abstracts and full text.
2. **Curate** — every numeric test condition is hand-copied from source text with a quote and locator (`data/test_conditions.csv`).
3. **Rank** — five documented dimensions (atmosphere match, microgravity evidence, flow, diagnostics, recency); missing data reduces *coverage*, never invents a value.
4. **Check** — Habitat Checker computes ppO₂ and compares with Test 1 (21.1 kPa) and the exploration atmosphere (19.2 kPa).
5. **Interpret** — hybrid retrieval (Gemini embeddings + TF-IDF) over 222 passages; six reviewed answers plus grounded generation with `[S#]` citations and a cache.

### Data and sources

- PSI repository — 24 investigations, metadata and objectives.
- NTRS — Saffire, BASS, FLEX, SAME, CFI, SLICE, ACME abstracts and full text.
- NASA-STD-6001B — Test 1 envelope (30% O₂ / 70.3 kPa → 21.1 kPa ppO₂).
- JSC 29353 — flammability configuration analysis.
- 2015 Researcher's Guide to Combustion Science.
- Apollo 1, Apollo 13, Mir fire, NASA spin-off pages for prevention/detection/suppression lessons and Earth applications.

Full table in `SOURCES.md`; provenance and limits in `README.md`.

### Technical approach

Python 3.11, Streamlit 1.67, pandas 3.1, Plotly 7.1, scikit-learn TF-IDF fallback, google-genai 3.0 (`gemini-3.5-flash-lite`, `gemini-embedding-001`). Data is rebuilt by reproducible scripts in `scripts/`; the app reads CSVs at runtime and runs without an API key. Eight pytest smoke tests enforce the data contract (quoted conditions, real investigation IDs, deterministic ranking, coverage behaviour).

### Limitations

- Prototype decision support, not fire-safety certification.
- No partial-gravity flight data in PSI; lunar/Mars behaviour is bounded by argument, not measured.
- 1-g upward-propagation screening is not conservative for low gravity.
- Most public PSI records omit numeric conditions; absence is reported as zero coverage.
- Ranking weights are expert-defined and adjustable, not NASA-endorsed.
- AI answers are grounded but require human review.

### What is next

- Curate the remaining condition rows from NTRS full text as it is digitised.
- Add partial-gravity data when LUCI/FM2 results are public.
- Replace expert weights with a sensitivity analysis over multiple stakeholder profiles.
- Validate the design rules with fire-safety engineers.

### Built with

Python, Streamlit, pandas, Plotly, scikit-learn, google-genai, NASA PSI API, NTRS API, pypdf.

### Credits

Data and imagery © NASA (PSI, NTRS, NASA standards). NASA does not endorse this project. AI coding assistance used; disclosed in the README. MIT licence.

---

## 3. Video

Script and captions: `docs/VIDEO_SCRIPT.md`. Captions only, ~2 minutes, YouTube unlisted.

---

## 4. Judging map

| Criterion | Where to point |
|---|---|
| **Impact** | Habitat fire risk; concrete design rules (ventilation, smoke detection, suppression margins); Earth spin-offs from NASA fire technology |
| **Creativity** | SI workflow from API to cited answer; coverage-aware ranking that refuses to fill gaps; ppO₂-native comparison; advisor that says "not in the evidence base" |
| **Technical validity** | Quoted conditions with locators; NASA-STD-6001B numbers; 1-g vs low-g caveat; deterministic tests; blank ≠ zero policy |
| **Relevance** | All 24 PSI combustion investigations; prevention/detection/suppression pillars; summarise, compare, rank, interpret |
| **Presentation** | Four-tab narrative, screenshots, 2-minute captioned video, README with architecture and limits |
