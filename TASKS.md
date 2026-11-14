# TASKS — Flame in Freefall

> **Rule:** Do not start project work before the official event start. Phase 0 is preparation only.
>
> **Priority:** P0 = must ship · P1 = important · P2 = stretch
>
> **Event start:** _[confirm local schedule]_

---

## Phase 0 — Before the event (allowed prep only)

### Logistics

- [ ] P0 Confirm local event start date/time and submission deadline.
- [ ] P0 Confirm solo registration is valid for the local event.
- [ ] P0 Confirm the Resources tab release time on Friday, November 13.
- [ ] P0 Create or verify GitHub account and repository access.
- [ ] P0 Create or verify Streamlit Community Cloud account.
- [ ] P0 Create a PSI account if raw-data access requires it.
- [ ] P0 Set `GEMINI_API_KEY` locally.
- [ ] P0 Verify `.venv` and `requirements.txt` install cleanly.

### Learning and planning

- [ ] P0 Read `ChallengeRef.txt` fully; annotate the three objectives.
- [ ] P0 Read the PSI pages for the 12 core investigations.
- [ ] P0 Read NTRS abstracts for the core investigations.
- [ ] P1 Bookmark PSI, NTRS, NASA-STD-6001B, and JSC 29353.
- [ ] P1 Review the prevention / detection / suppression framing.
- [ ] P1 Review the Moon base 30%+ O₂ at ≤10.2 psi and spacesuit 100% O₂ at 4.3 psi facts.
- [ ] P1 Review the partial-gravity data gap.
- [ ] P1 Practice Streamlit + Plotly + Gemini with an unrelated toy app (optional).
- [ ] P1 Test Streamlit Cloud deployment with the toy app (optional).
- [ ] P1 Rehearse the 90-second demo narrative on paper.
- [ ] P2 Draft the README structure on paper.

### Do not do yet

- [ ] Do **not** create the app.
- [ ] Do **not** curate `investigations.csv` or `test_conditions.csv`.
- [ ] Do **not** generate summaries, corpus, or `qa_cache.json`.
- [ ] Do **not** create challenge-specific images or assets.
- [ ] Do **not** initialize the project git repo before the event start.

---

## Phase 1 — Friday, November 13 (resources release)

- [ ] P0 Read the official Resources tab.
- [ ] P0 Note any mandatory requirements or provided files.
- [ ] P0 Map each resource to the two-table schema.
- [ ] P0 Record source URLs, PSI IDs, and NTRS IDs in `SOURCES.md`.
- [ ] P1 Update `DECISIONS.md` if the official resources change the scope.
- [ ] P1 Check whether the local event starts Friday evening.
- [ ] P1 If work is allowed: initialize the repo and make the first commit.
- [ ] P2 If work is not allowed: stop after reading and mapping.

---

## Phase 2 — Day 1: Saturday, November 14

### Setup

- [ ] P0 Initialize git repo; first commit with timestamp.
- [ ] P0 Create folders: `data/`, `corpus/`, `tabs/`, `scripts/`, `.streamlit/`.
- [ ] P0 Add `.gitignore` entries for `.venv/`, `.env`, `.streamlit/secrets.toml`.
- [ ] P0 Create `.streamlit/secrets.toml` with `GEMINI_API_KEY`.
- [ ] P0 Create a minimal `app.py` that runs.

### Data

- [ ] P0 Curate 12 core investigations in `data/investigations.csv`.
- [ ] P0 Curate 25–30 test points in `data/test_conditions.csv`.
- [ ] P0 Add `value_type`, `source_locator`, and `confidence` for every numeric value.
- [ ] P0 Build `data/sources.json`.
- [ ] P0 Run `scripts/validate_data.py`.
- [ ] P1 Verify units: %, kPa, cm/s, mm/s, mm, s.
- [ ] P1 Add image URLs and credits; use icons if images are missing.

### App

- [ ] P0 Build sidebar mission context.
- [ ] P0 Build Experiment Library tab.
- [ ] P0 Build Compare & Rank tab.
- [ ] P0 Add evidence-priority scoring with weight sliders.
- [ ] P0 Add matched comparison mode.
- [ ] P1 Add “Explain this view” button.

### AI

- [ ] P0 Build `corpus/chunks.jsonl`.
- [ ] P0 Build TF-IDF retrieval.
- [ ] P0 Build Gemini client with structured JSON output.
- [ ] P0 Generate and human-review summaries.
- [ ] P0 Build Evidence Advisor.
- [ ] P0 Add `qa_cache.json` with 10+ canonical answers.
- [ ] P0 Add offline fallback and 429 handling.
- [ ] P1 Add citation chips and retrieved-evidence expander.

### Habitat

- [ ] P0 Build Habitat Checker inputs.
- [ ] P0 Compute ppO₂.
- [ ] P0 Add NASA-STD-6001 Test 1 envelope check.
- [ ] P0 Add >30% O₂ warning.
- [ ] P0 Add nearest-experiment evidence.
- [ ] P0 Add risk contributors and design rules.
- [ ] P1 Add partial-gravity caveat.
- [ ] P1 Add Earth spin-off panel.

### End of day

- [ ] P0 Test the app from a fresh terminal.
- [ ] P0 Commit with a clear message.
- [ ] P0 Update `PROGRESS.md`.
- [ ] P0 List blockers for Day 2.

---

## Phase 3 — Day 2: Sunday, November 15

### QA

- [ ] P0 Re-check every number against its source locator.
- [ ] P0 Check units and conversions.
- [ ] P0 Check citations and links.
- [ ] P0 Check the >30% O₂ / NASA-STD-6001 statement.
- [ ] P0 Check the partial-gravity caveat.
- [ ] P0 Check disclaimers: prototype, not certified.
- [ ] P0 Test offline mode and simulated 429.
- [ ] P0 Test empty states and missing data.

### Presentation

- [ ] P0 Finalize the 90-second demo.
- [ ] P0 Rehearse twice.
- [ ] P0 Record the 2-minute video.
- [ ] P0 Take screenshots for the submission page.
- [ ] P1 Check colorblind-safe palette and alt text.

### Submission

- [ ] P0 Write README: overview, data, methods, limitations, credits.
- [ ] P0 Add repo URL and demo URL.
- [ ] P0 Add video URL.
- [ ] P0 Add data-source credits and licenses.
- [ ] P0 Add AI-assistance disclosure.
- [ ] P0 Check no secrets are committed.
- [ ] P0 Verify a fresh clone installs from `requirements.txt`.
- [ ] P0 Submit early.
- [ ] P1 Keep a backup ZIP of the project and video.

---

## Phase 4 — Stretch goals (only after P0 is done)

- [ ] P2 Add ACME CLD Flame.
- [ ] P2 Add ACME E-FIELD Flames.
- [ ] P2 Add ACME S-Flames.
- [ ] P2 Add CFI.
- [ ] P2 Add DAFT / DAFT-2.
- [ ] P2 Add SLICE.
- [ ] P2 Add Utilization of SAME Data.
- [ ] P2 Add a similarity map.
- [ ] P2 Add investigation images.
- [ ] P2 Add a downloadable filtered CSV.
- [ ] P2 Add keyboard/accessibility improvements.

---

## Definition of done

- [ ] 12 core investigations sourced.
- [ ] 25–30 test points sourced.
- [ ] Four tabs working.
- [ ] Habitat Checker computes ppO₂ and flags >30% O₂.
- [ ] Advisor returns cited answers; 10+ cached Q&A.
- [ ] Offline mode tested.
- [ ] README complete.
- [ ] Video recorded.
- [ ] Submission completed before the deadline.
