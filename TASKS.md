# TASKS — Flame in Freefall

> **Priority:** P0 = must ship · P1 = important · P2 = stretch
> **Event:** Sat 14 Nov 09:00 → Sun 15 Nov 23:59 local · target submit 20:00

---

## Done

### Setup

- [x] P0 Git repo initialized inside the event window; remote `Victor0530/flame-in-freefall`.
- [x] P0 `data/`, `corpus/`, `tabs/`, `scripts/`, `tests/`, `.streamlit/` created.
- [x] P0 `.gitignore` covers `.venv/`, `.env`, `.streamlit/secrets.toml`.
- [x] P0 `GEMINI_API_KEY` in `secrets.toml`; verified `gemini-3.5-flash-lite`.
- [x] P0 `app.py` runs with four tabs.
- [x] P0 Theme (`lib/theme.py`, `.streamlit/config.toml`).

### Data

- [x] P0 All 24 PSI combustion investigations ingested (`data/investigations.csv`).
- [x] P0 26 curated condition rows with quote + locator (`data/test_conditions.csv`).
- [x] P0 8 investigations with at least one numeric condition.
- [x] P0 NTRS abstracts and Researcher's Guide extracted into `data/corpus/`.
- [x] P1 Units normalised: %, kPa, cm/s.

### App

- [x] P0 Sidebar mission context, material focus, comparison tray, data status.
- [x] P0 Experiment Library with pillar/program/search/flight filters.
- [x] P0 Compare & Rank with adjustable weights, coverage, evidence labels.
- [x] P0 Condition matrix with source locator and quote.
- [x] P0 Habitat Checker: ppO₂ gauge, Test 1 envelope, exploration atmosphere, design rules.
- [x] P1 Evidence expanders (Saffire, BASS, CFI-G, SAME).

### AI

- [x] P0 `chunks.jsonl` (198 passages) and `embeddings.npz` (768-d).
- [x] P0 Hybrid retrieval: Gemini embeddings + TF-IDF fallback, relative score filter.
- [x] P0 `data/faq.json` with 6 human-reviewed answers.
- [x] P0 Grounded generation with `[S#]` citations and prompt v2 constraints.
- [x] P0 Answer cache (`data/cache/answers.json`).
- [x] P0 Offline extractive fallback verified.
- [x] P1 Citation chips and retrieved-passage expander.

### QA and docs

- [x] P0 8 pytest smoke tests (data contract, ranking, FAQ coverage).
- [x] P0 Number/unit/source review pass.
- [x] P0 >30% O₂ and 1-g-vs-low-g wording checked.
- [x] P0 Prototype disclaimer, AI disclosure, no-endorsement note.
- [x] P0 README complete.
- [x] P0 Screenshots captured in `docs/screenshots/`.
- [x] P0 Video script with captions (`docs/VIDEO_SCRIPT.md`).

---

## Remaining

### Submission (P0)

- [ ] Deploy to Streamlit Cloud. **Owner: user.**
- [ ] Fresh-clone check on a clean environment.
- [ ] Record 2-minute captioned video.
- [ ] Upload video (unlisted) and paste link into `SUBMISSION.md`.
- [ ] Fill project page fields from `SUBMISSION.md` §2.
- [ ] Test all links logged out.
- [ ] Submit before 20:00.
- [ ] Backup ZIP of code + video.

### Optional polish (P1/P2, only with spare time)

- [ ] P1 Earth spin-off panel in Habitat Checker.
- [ ] P1 Downloadable filtered CSV from Library.
- [ ] P2 Similarity map across investigations.
- [ ] P2 Colourblind simulation check.
- [ ] P2 Mobile layout check.

---

## Definition of done

- [x] 24 investigations sourced (exceeds the 12-core target).
- [x] 26 test points sourced with quotes.
- [x] Four tabs working.
- [x] Habitat Checker computes ppO₂ and flags >30% O₂.
- [x] Advisor returns cited answers; 6 reviewed + generated fallback.
- [x] Offline mode tested.
- [x] README complete.
- [ ] Video recorded.
- [ ] Submission completed before the deadline.
