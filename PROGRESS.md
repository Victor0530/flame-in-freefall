# PROGRESS — Flame in Freefall

> Update at the end of each work block. Factual and timestamped.
>
> **Event start:** Saturday, November 14, 2026, 09:00
> **First commit:** 2026-11-15 01:10 (`24d9ea7`)

---

## Status snapshot

| Area | Status | Last updated | Notes |
|---|---|---|---|
| Compliance / git | Done | 2026-11-15 02:25 | Public repo, event-window history |
| Data curation | Done | 2026-11-15 01:55 | 24 records, 26 condition rows, 8 numeric |
| Sources / citations | Done | 2026-11-14 19:00 | R1–R10 mapped; PSI IDs verified |
| Experiment Library | Done | 2026-11-15 02:00 | Filters, search, comparison tray |
| Compare & Rank | Done | 2026-11-15 02:10 | Coverage-aware ranking, condition matrix |
| Habitat Checker | Done | 2026-11-15 01:30 | ppO₂ gauge, Test 1, design rules |
| Evidence Advisor | Done | 2026-11-15 02:15 | Reviewed answers + grounded generation + cache |
| Offline mode | Done | 2026-11-15 02:20 | Extractive fallback verified |
| README | Done | 2026-11-15 02:05 | Architecture, provenance, limits |
| Demo video | Not started | — | Script ready in `docs/VIDEO_SCRIPT.md` |
| Submission | In progress | — | Awaiting video + cloud deploy |

**Status values:** Not started · In progress · Blocked · Done · Cut

---

## Metrics

| Metric | Target | Actual |
|---|---|---|
| Investigations curated | 12 | 24 (19 flight, 5 ground) |
| Test-condition rows | 25–30 | 26 (8 numeric investigations) |
| Sources with URL + locator | 12+ | 24 PSI + 31 NTRS |
| Corpus passages | 100+ | 198 (23,577 words) |
| Tabs working | 4 | 4 |
| Reviewed Q&A | 10+ | 6 (+ grounded generation) |
| Gemini calls tested | 5+ | 4 |
| Offline-mode tests | 1 | 2 (extractive + cache) |
| Automated tests | — | 8 passing |
| Bugs open | 0 | 0 |

---

## Daily log — Friday, November 13

| Time | Done | Blocker | Next |
|---|---|---|---|
| — | Resources release read; R1–R10 mapped in `RESOURCE_REVIEW.md` | — | Wait for event start |

---

## Daily log — Saturday, November 14

| Time | Done | Blocker | Next |
|---|---|---|---|
| 19:00 | Official resources read; PSI API + IDs verified | Repo not initialized | Init git, ingest data |
| 23:30 | Scope confirmed: all 24 investigations, curated conditions for the core set | — | Build after key |

---

## Daily log — Sunday, November 15

| Time | Done | Blocker | Next |
|---|---|---|---|
| 00:45 | Gemini key verified; `gemini-3.5-flash-lite` responds | — | Repo init |
| 01:10 | Git initialized; first commit `24d9ea7` | — | PSI ingestion |
| 01:14 | 24 records → `data/investigations.csv` | — | Dashboard shell |
| 01:30 | Dashboard v1: sidebar, KPIs, Library, Habitat Checker | No curated conditions | Curate test conditions |
| 01:55 | `test_conditions.csv` (26 rows, quoted) + `lib/scoring.py` | — | Compare tab |
| 02:00 | Compare & Rank with coverage, matrix, weight sliders | — | Corpus |
| 02:10 | 198-passage corpus + embeddings; advisor with reviewed answers | — | Prompt hardening |
| 02:15 | Prompt v2; grounded answer verified; cache | — | Docs |
| 02:20 | Offline path verified; 8 tests passing | — | README |
| 02:30 | README, screenshots, video script, submission copy; pushed | — | Video + deploy |

---

## Blockers

| # | Blocker | Impact | Workaround | Status |
|---|---|---|---|---|
| 1 | Streamlit Cloud deploy | Submission demo URL | Local run + screenshots; user deploys | Open (user) |
| 2 | Demo video not recorded | Submission needs video | Script and shots ready | Open |
| 3 | Most PSI records lack numeric conditions | Ranking coverage 55% for several | Shown as coverage, never guessed | Accepted |

---

## Commit log

| Time | Commit | What changed |
|---|---|---|
| 2026-11-15 01:10 | `24d9ea7` | Initialize repo with planning docs and resource review |
| 2026-11-15 01:14 | `8684191` | PSI ingestion script + `investigations.csv` (24 records) |
| 2026-11-15 01:22 | `9876e43` | Dashboard shell: four tabs, theme, library, habitat |
| 2026-11-15 01:35 | `ed02fdf` | Polish: encoding, filters, habitat messaging, progress log |
| 2026-11-15 02:25 | _see `git log`_ | Curation, ranking, advisor, tests, README, screenshots |

---

## Compliance evidence

| Item | Value |
|---|---|
| Local event official start | 2026-11-14 09:00 |
| Repo initialized | 2026-11-15 01:10 |
| First commit | 2026-11-15 01:10 (`24d9ea7`) |
| First project file created | 2026-11-14 19:00 (`RESOURCE_REVIEW.md`, `SOURCES.md`, `DECISIONS.md`) |
| Resources read | 2026-11-14 19:00 |
| Repo public | https://github.com/Victor0530/flame-in-freefall |
| Submission time | — |

---

## End-of-day checklist

### Day 1

- [x] App runs from a fresh terminal.
- [x] Data validates.
- [x] At least two tabs work.
- [x] Advisor returns one cited answer.
- [x] Offline fallback exists.
- [x] Commit made.
- [x] Blockers listed for Day 2.

### Day 2

- [ ] All P0 tasks complete (video + deploy remain).
- [x] Numbers and citations checked.
- [x] Offline mode tested.
- [ ] Video recorded.
- [x] README complete.
- [ ] Submission completed.
- [ ] Backup ZIP saved.
