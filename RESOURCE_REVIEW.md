# RESOURCE REVIEW — official Resources tab

> **Read:** 2026-11-14, 19:00 local (event is live; submission window Sat 09:00 → Sun 23:59 local).
> **Source:** `ChallengeResource.txt` (10 links) + live checks of PSI, NASA, NTRS, NTSS.
> **Purpose:** reconcile the official resources with `PLAN.md`, `SOURCES.md`, and `DATA_SCHEMA.md` before curation starts.

---

## 1. What was actually released

| # | Resource | Type | What it gives you | Where it goes |
|---|---|---|---|---|
| R1 | [PSI combustion search](https://psi.nasa.gov/physci/repo/search?q=combustion&data_source=psi&data_type=investigation) | Data | The only dataset. Metadata for every combustion investigation + raw/derived data files. | Data layer, library, corpus |
| R2 | [NASA Combustion Science](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/) | Background | One-page summary + 1–2 page PDF fact sheet per experiment; hardware (CIR, MDCA, MSG); current experiments FM2, SoFIE, FLARE | Investigation narratives, hardware map, images |
| R3 | [ScienceCasts: Power of Studying Combustion on the ISS](https://www.youtube.com/watch?v=W1oXykoz9zg) | Video (3.6 min) | Plain-language framing of why microgravity combustion matters | Demo intro / b-roll; not data |
| R4 | [Researcher's Guide to ISS Combustion Science](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/) (Oct 2015, 50+ pp) | Background (PDF 1.5 MB) | Authoritative review of investigations, facilities, fire-safety framing | Corpus + methodology citations |
| R5 | [Apollo 1](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) | History / lessons | 1967 pre-launch fire in 100% O₂; materials and ground-test lessons | Prevention narrative, risk framing |
| R6 | [Apollo 13](https://sma.nasa.gov/sma-disciplines/accllp/apollo-13) | History / lessons | O₂ tank explosion en route to the Moon; system-failure lessons | Risk framing (not combustion data) |
| R7 | [Mir fire, 1997](https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/) | History / lessons | Oxygen-generator fire; detection/suppression response | Detection + suppression narrative |
| R8 | [Fireman's air tanks](https://spinoff.nasa.gov/node/9582) | Earth spin-off | 1970s spacesuit tech → firefighter breathing gear | Earth applications panel |
| R9 | [Fire detector](https://spinoff.nasa.gov/node/9407) | Earth spin-off | Shuttle smoke detector that discriminates smoke vs. dust → fewer nuisance alarms | Detection narrative + Earth panel |
| R10 | [Fire-resistant attire](https://spinoff.nasa.gov/node/9918) | Earth spin-off | 1980s spacesuit materials → firefighter clothing | Earth applications panel |

**Shape of the release:** 2 data/background sources, 1 video, 3 history case studies, 3 Earth spin-offs.
There is **no curated CSV, no sample test-condition table, and no API documentation**.

---

## 2. What is *not* in the resource set (but the build needs)

| Missing | Status | Decision |
|---|---|---|
| NASA-STD-6001B (flammability test standard) | Public on NTSS: <https://standards.nasa.gov/standard/NASA/NASA-STD-6001> — rev. **B w/Change 3**, active, change dated 2025-06-09 | Use as a **supporting standard**, clearly not labelled a challenge resource |
| JSC 29353 (Flammability Configuration Analysis) | Public: rev. **D**, Dec 2024, <https://standards.nasa.gov/standard/JSC/JSC-29353> | Optional; use only if it adds a rule you can cite |
| Partial-gravity combustion data | Confirmed absent by the challenge text; LUCI/FM2 are future | Keep the caveat; do not interpolate silently |
| Small pre-built dataset | None | Build from PSI metadata + NTRS papers (see §4) |

---

## 3. Verified atmosphere numbers (fix these before the demo)

| Condition | O₂ % | Total pressure | ppO₂ | Source |
|---|---|---|---|---|
| Earth "ambient" per NASA-STD-6001B §6.3.3 | 20.9 | 101.4 kPa (14.7 psia) | 21.2 kPa | NASA-STD-6001B |
| Spacesuit | 100 | 4.3 psi = 29.6 kPa | 29.6 kPa | Challenge text |
| NASA-STD-6001B Test 1 historical envelope | **30** | **10.2 psia = 70.3 kPa** | **21.1 kPa** | NTRS 20180004258; task-book summary |
| NASA "exploration atmosphere" (Moon/Mars habitat) | **34** | **8.2 psia = 56.5 kPa** | **19.2 kPa** | NTRS 20220009546; 20230015380 |
| Challenge's Moon-base statement | ≥30 | ≤10.2 psi | — | `ChallengeRef.txt` |

**Correction to `PLAN.md` §7:** the demo uses "34% O₂, 70.3 kPa". That combination is **not a NASA design point** and the claim "outside NASA-STD-6001 Test 1 envelope" is misleading. Use **34% O₂ / 56.5 kPa** for the exploration preset, and phrase the result as:

> "This atmosphere exceeds the O₂ concentration of NASA-STD-6001B's historical Test 1 point (30% at 70.3 kPa). No PSI test was run at this combination; the nearest evidence is …"

Do **not** present a binary "pass/fail certification". Test 1 is a 1-g upward-propagation test and is not conservative for low-g; say that explicitly.

`ppO₂ = O₂% / 100 × total pressure (kPa)` — compute, never hand-enter.

---

## 4. PSI access — the unlock

The repository is an Angular app, but it talks to a public JSON API. No key required.

```text
Search:  https://psi.nasa.gov/geode-py/ws/repo/search?term=combustion&source=psi&type=investigation&size=50
Detail:  https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-159   (slow/flaky in browser; retry)
Images:  https://psi.nasa.gov/geode-py/ws/investigations/PSI-159/image
```

Fields returned per investigation: `Accession`, `Title`, `Acronym`, `Person`, `Keywords`, `Flight Platform`,
`Research Area`, `SubResearch Area`, `Project Type`, `Objectives`, `Approach`, `Hypothesis`,
`Research Impacts/Earth Benefits`, `Experiment Hardware`, `Publication Title/Author List`, `Data Source Type`,
start/end dates, public release date.

**Tested:** `term=combustion` returns **26 records**. Two are false positives (PSI-181 materials, PSI-108 fluid physics) →
**24 combustion records = 19 flight/microgravity + 5 ground studies**. That is the whole public combustion collection.

### 19 flight investigations (verified IDs)

| PSI | Investigation | Pillar | Core? | Hardware |
|---|---|---|---|---|
| PSI-26 | BASS | Prevention | Core | MSG flow duct |
| PSI-25 | BASS-II | Prevention | Core | MSG flow duct |
| PSI-98 | Saffire-I | Prevention | Core | Cygnus |
| PSI-99 | Saffire-II | Prevention | Core | Cygnus |
| PSI-100 | Saffire-III | Prevention | Core | Cygnus |
| PSI-69 | FLEX | Suppression | Core | MDCA / CIR |
| PSI-68 | FLEX-2 | Suppression | Core | MDCA / CIR |
| PSI-102 | SAME | Detection | Core | MSG |
| PSI-101 | SAME-R | Detection | Core | MSG |
| PSI-20 | ACME BRE | Prevention | Core | ACME / CIR |
| PSI-159 | ACME CFI-G | Prevention | Core | ACME / CIR |
| PSI-107 | SPICE | Prevention | Core | MSG flow duct |
| PSI-21 | ACME CLD Flame | Prevention | Optional | ACME / CIR |
| PSI-22 | ACME E-FIELD Flames | Prevention | Optional | ACME / CIR |
| PSI-23 | ACME s-Flame | Prevention | Optional | ACME / CIR |
| PSI-39 | CFI (droplets) | Prevention | Optional | MDCA / CIR |
| PSI-106 | SLICE | Prevention | Optional | MSG flow duct |
| PSI-47 | DAFT / DAFT-2 | Detection | Optional | MSG |
| PSI-10 | ACME Flame Design | Prevention | **New** | ACME / CIR |

### 5 ground studies (the "other investigations in PSI" the challenge mentions)

| PSI | Study | Reuses |
|---|---|---|
| PSI-60 | Computational/experimental analysis of SPICE data sets | SPICE |
| PSI-62 | Concurrent flame-spread modeling vs. BASS | BASS |
| PSI-115 | SAME smoke-generation modeling | SAME |
| PSI-117 | Cool-flame CFD using FLEX data | FLEX |
| PSI-142 | Cool-flame transitions from FLEX data | FLEX |

### Corrections to `SOURCES.md`

| Was | Correct |
|---|---|
| SPICE (ground) = PSI-60 | SPICE = **PSI-107**; PSI-60 is a ground reanalysis of SPICE |
| SAME-R = PSI-101 (correct) | SAME = **PSI-102**, SAME-R = **PSI-101** |
| DAFT assumed absent | DAFT/DAFT-2 = **PSI-47**, present in PSI |
| — | ACME Flame Design = **PSI-10** (not in the plan) |

Also: PSI `Investigation Start/End Date` values are **award/investigation periods, not flight dates** (e.g. Saffire-I shows 2001–2008). Do not display them as mission dates without checking. `Person` is a flattened name string; parse carefully or omit.

### Per-investigation files

Investigation pages list small artifacts (e.g. PSI-159: metadata ISA `.zip`, final report PDF, engineering report PDF) alongside the large raw/derived datasets. **Use the metadata + reports; skip the multi-GB data.** This preserves decision D11 and still gives real source locators.

### NTRS (corpus gold)

```text
Search:   https://ntrs.nasa.gov/api/citations/search?q=<query>&page.size=20
Download: https://ntrs.nasa.gov/api/citations/<id>/downloads/<id>.pdf
Fulltext: https://ntrs.nasa.gov/api/citations/<id>/downloads/<id>.txt   ← use this for chunks
```

NTRS returns `abstract` directly and often a plain-text fulltext. That removes most PDF parsing risk and makes the
TF-IDF corpus cheap to build.

---

## 5. What this changes in the plan

1. **Scope is fine, but under-claimed.** All 12 core and all 7 optional investigations exist in PSI. The library can
   ship with all **19 flight investigations** (metadata is free from the API) while only the core 12 get hand-curated
   test-condition rows. That is a much stronger "coverage" story for Relevance judging.
2. **Add one tab-level panel, not a tab:** *Related ground studies* (5 records) and *Earth spin-offs* (R8–R10).
   The challenge explicitly calls out Earth applications; the resources hand you three citable examples.
3. **History is evidence, not decoration.** Apollo 1 (materials + 100% O₂), Mir (oxygen generator), Apollo 13
   (system failure) each map to a prevention/detection/suppression claim. One sentence + link is enough.
4. **Fix the Habitat Checker logic** per §3. Keep ppO₂, add the two reference atmospheres, drop the binary
   "certified/not certified" framing.
5. **Data pipeline is simpler than planned.** PSI JSON → `investigations.csv`; NTRS abstract/fulltext → corpus.
   Only `test_conditions.csv` needs manual extraction.
6. **No change to the 4-tab architecture** (Library, Compare & Rank, Habitat Checker, Advisor). Good.

---

## 6. Judging map (1–5 per criterion)

| Criterion | What to show | Resource hook |
|---|---|---|
| **Impact** | Moon/Mars habitat risk, design rules, Earth spin-offs | R8–R10, §3 numbers |
| **Creativity** | SI workflow: evidence ranking + habitat checker + cited advisor + "explain this view" | R1 + R2 |
| **Validity** | Source locator per value, measured/reported/estimated, ppO₂ math, low-g caveat, partial-g gap | R4, NASA-STD-6001B |
| **Relevance** | Summarize / rank / interpret; all 19 flight investigations; prevention/detection/suppression | R1 |
| **Presentation** | 90-second story, clean visuals, offline backup video | R3, R5–R7 |

---

## 7. Rebaselined schedule (from Sat 19:00)

> Day-1 morning/most of afternoon is gone. Cut the optional 7's **curation** (keep their metadata rows) and the
> similarity map. Protect: citations, Habitat Checker, offline mode, video.

### Saturday 19:00 → 01:00 (6 h)

| Time | Work |
|---|---|
| 19:00–19:30 | `git init`, folders, `.gitignore`, `secrets.toml`, minimal `app.py`, first commit |
| 19:30–21:00 | `scripts/fetch_psi.py` → `investigations.csv` (19 rows); start `test_conditions.csv` (24 rows, core 12) |
| 21:00–22:30 | Sidebar mission context + Experiment Library |
| 22:30–00:00 | Compare & Rank (matched conditions, evidence score with visible weights) |
| 00:00–01:00 | Corpus (NTRS fulltext + PSI objectives + R4) + TF-IDF retrieval |

### Sunday 09:00 → 21:00 (submit by 21:00, not 23:59)

| Time | Work |
|---|---|
| 09:00–11:00 | Habitat Checker + design rules + Earth spin-off panel |
| 11:00–12:30 | Gemini advisor, structured JSON, cache, offline fallback |
| 12:30–13:30 | QA: every number → locator; units; §3 statements |
| 13:30–15:00 | Polish, empty states, screenshots |
| 15:00–16:00 | Rehearse + record 2-min video |
| 16:00–18:00 | README, submission page, deploy to Streamlit Cloud |
| 18:00–21:00 | Buffer, fresh-clone test, submit; keep backup ZIP |

---

## 8. Next 60 minutes

- [ ] Confirm the **local** submission deadline and whether judging is in person.
- [ ] `git init` + first commit (compliance evidence).
- [ ] Run the PSI search endpoint once and save the JSON as `data/raw/psi_combustion.json` for reproducibility.
- [ ] Build `investigations.csv` from the API — do not hand-type 19 rows.
- [ ] Pick the 24 test points **before** writing UI code; they drive every chart.
- [ ] Fix the demo atmosphere to 34% / 56.5 kPa in `PLAN.md` and the video script.