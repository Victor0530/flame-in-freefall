# PROGRESS — Flame in Freefall

> Update this file at the end of each work block. Keep it factual and timestamped.
>
> **Event start:** Saturday, November 14, 2026, 09:00 (submission window)
> **First commit:** 2026-11-15 01:10 (`24d9ea7`)

---

## Status snapshot

| Area | Status | Last updated | Notes |
|---|---|---|---|
| Compliance / git | Done | 2026-11-15 01:10 | Repo initialized after resources review |
| Data curation | In progress | 2026-11-15 01:14 | 24 records ingested from PSI API; test conditions pending |
| Sources / citations | Done | 2026-11-14 19:00 | R1–R10 mapped; PSI IDs verified |
| Experiment Library | Done (v1) | 2026-11-15 01:20 | Filters, search, comparison selection |
| Compare & Rank | In progress | 2026-11-15 01:24 | Empty state, matrix; scoring disabled until data |
| Habitat Checker | Done (v1) | 2026-11-15 01:29 | ppO₂ gauge, Test 1 envelope, design rules |
| Evidence Advisor | Not started | — | Placeholder; needs corpus + cache |
| Offline mode | Not started | — | Planned fallback |
| README | Not started | — | Public documentation |
| Demo video | Not started | — | 2 minutes |
| Submission | Not started | — | Submit early |

**Status values:** Not started · In progress · Blocked · Done · Cut

---

## Metrics

| Metric | Target | Actual |
|---|---|---|
| Core investigations curated | 12 | 0 (24 metadata rows loaded) |
| Test-condition rows | 25–30 | 0 |
| Sources with URL + locator | 12+ | 24 PSI records |
| Tabs working | 4 | 3 (Advisor placeholder) |
| Cached Q&A | 10+ | 0 |
| Gemini calls tested | 5+ | 1 (key + model verified) |
| Offline-mode tests | 1 | 0 |
| Bugs open | 0 | 0 |

---

## Daily log — Friday, November 13

| Time | Done | Blocker | Next |
|---|---|---|---|
| — | Resources release read (R1–R10 mapped in `RESOURCE_REVIEW.md`) | — | Wait for event start |

---

## Daily log — Saturday, November 14

| Time | Done | Blocker | Next |
|---|---|---|---|
| 19:00 | Official resources read; PSI API + IDs verified | Repo not initialized | Init git, pull PSI metadata |
| 23:30 | Scope confirmed: core 12 + 19-flight library | — | Build after key |

> Day-1 morning block did not happen; schedule replanned in `RESOURCE_REVIEW.md` §7.

---

## Daily log — Sunday, November 15

| Time | Done | Blocker | Next |
|---|---|---|---|
| 00:45 | Gemini key verified; `gemini-3.5-flash-lite` responds | — | Repo init |
| 01:10 | Git initialized; first commit `24d9ea7` | — | PSI ingestion |
| 01:14 | PSI ingestion: 24 records → `data/investigations.csv` | — | Dashboard shell |
| 01:30 | Dashboard v1: sidebar, KPIs, Library, Habitat Checker | Curated test conditions missing | Build `test_conditions.csv` |

---

## Blockers

| # | Blocker | Impact | Workaround | Status |
|---|---|---|---|---|
| 1 | Test conditions not curated | No numeric comparison or ranking | Ship metadata-only evidence view; curate 24 points | Open |
| 2 | No corpus / AI yet | Advisor disabled | TF-IDF + Gemini with cache | Open |
| 3 | Deadline 23:59 today | Fixed | Submit by 20:00 | Open |

---

## Commit log

| Time | Commit | What changed |
|---|---|---|
| 2026-11-15 01:10 | `24d9ea7` | Initialize repo with planning docs and resource review |
| 2026-11-15 01:14 | `8684191` | PSI ingestion script + `investigations.csv` (24 records) |
| 2026-11-15 01:22 | `9876e43` | Dashboard shell: four tabs, theme, library, habitat |

---

## Compliance evidence

| Item | Value |
|---|---|
| Local event official start | 2026-11-14 09:00 (submission window per spaceappschallenge.org) |
| Repo initialized | 2026-11-15 01:10 |
| First commit | 2026-11-15 01:10 (`24d9ea7`) |
| First project file created | 2026-11-14 19:00 (`RESOURCE_REVIEW.md`, `SOURCES.md`, `DECISIONS.md` updates) |
| Resources read | 2026-11-14 19:00 |
| Submission time | — |

---

## End-of-day checklist

### Day 1

- [x] App runs from a fresh terminal.
- [ ] Data validates.
- [x] At least two tabs work.
- [ ] Advisor returns one cited answer.
- [ ] Offline fallback exists.
- [x] Commit made.
- [x] Blockers listed for Day 2.

### Day 2

- [ ] All P0 tasks complete.
- [ ] Numbers and citations checked.
- [ ] Offline mode tested.
- [ ] Video recorded.
- [ ] README complete.
- [ ] Submission completed.
- [ ] Backup ZIP saved.
