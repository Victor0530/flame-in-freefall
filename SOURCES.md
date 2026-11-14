# SOURCES — Flame in Freefall

> One row per source. Use `S1`, `S2`, … in summaries, answers, and UI citations.
>
> **Rule:** every numeric value in the app must trace to a source locator.
>
> **Status:** `verified` means you opened the source and checked the value yourself.

---

## Source tracker

| ID | Investigation | Type | Title | URL / DOI | Locator | Used for | Confidence | Verified |
|---|---|---|---|---|---|---|---|---|
| S1 | | | | | | | | No |
| S2 | | | | | | | | No |
| S3 | | | | | | | | No |
| S4 | | | | | | | | No |
| S5 | | | | | | | | No |
| S6 | | | | | | | | No |
| S7 | | | | | | | | No |
| S8 | | | | | | | | No |
| S9 | | | | | | | | No |
| S10 | | | | | | | | No |
| S11 | | | | | | | | No |
| S12 | | | | | | | | No |

---

## Official challenge resources (released 2026-11-13)

Full mapping and what each resource is for: `RESOURCE_REVIEW.md`.

| ID | Resource | URL | Used for |
|---|---|---|---|
| R1 | PSI combustion search | `https://psi.nasa.gov/physci/repo/search?q=combustion&data_source=psi&data_type=investigation` | Primary dataset + metadata |
| R2 | NASA Combustion Science | `https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/` | Experiment fact sheets, hardware |
| R3 | ScienceCasts combustion video | `https://www.youtube.com/watch?v=W1oXykoz9zg` | Demo framing |
| R4 | Researcher's Guide (2015) | `https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/` | Background, corpus |
| R5 | Apollo 1 | `https://sma.nasa.gov/sma-disciplines/accllp/apollo-1` | Prevention lessons |
| R6 | Apollo 13 | `https://sma.nasa.gov/sma-disciplines/accllp/apollo-13` | Risk narrative |
| R7 | Mir fire (1997) | `https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/` | Detection/suppression lessons |
| R8 | Fireman's air tanks | `https://spinoff.nasa.gov/node/9582` | Earth spin-off |
| R9 | Fire detector | `https://spinoff.nasa.gov/node/9407` | Detection + Earth spin-off |
| R10 | Fire-resistant attire | `https://spinoff.nasa.gov/node/9918` | Earth spin-off |

## Known starting points

| Source | URL | Status | Notes |
|---|---|---|---|
| Challenge page | `https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/` | Verify | Official challenge statement |
| PSI repository | `https://psi.nasa.gov/` | Verified | Metadata via public JSON API (see `RESOURCE_REVIEW.md` §4) |
| NTRS | `https://ntrs.nasa.gov/` | Verified | Abstract + fulltext `.txt` via `/api/citations/` |
| NASA-STD-6001B w/Change 3 | `https://standards.nasa.gov/standard/NASA/NASA-STD-6001` | Verified | Test 1: 30% O₂ @ 70.3 kPa historical envelope |
| JSC 29353D (Dec 2024) | `https://standards.nasa.gov/standard/JSC/JSC-29353` | Verified | Flammability configuration analysis; optional |
| Exploration atmosphere | `https://ntrs.nasa.gov/citations/20220009546` | Verified | 56.5 kPa / 34% O₂ / 66% N₂ |

---

## Verified PSI identifiers (core 12)

Checked against the PSI JSON API on 2026-11-14. Full 24-record list: `RESOURCE_REVIEW.md` §4.

| Investigation | PSI ID | Status |
|---|---|---|
| BASS | PSI-26 | Verified |
| BASS-II | PSI-25 | Verified |
| Saffire-I | PSI-98 | Verified |
| Saffire-II | PSI-99 | Verified |
| Saffire-III | PSI-100 | Verified |
| FLEX | PSI-69 | Verified |
| FLEX-2 | PSI-68 | Verified |
| SAME | PSI-102 | Verified |
| SAME-R | PSI-101 | Verified |
| ACME BRE | PSI-20 | Verified |
| ACME CFI-G | PSI-159 | Verified |
| SPICE | PSI-107 | Verified |

> **Do not use PSI-60 for SPICE.** PSI-60 is a ground reanalysis of SPICE data.
> DAFT/DAFT-2 is PSI-47; ACME Flame Design is PSI-10.

---

## Candidate NTRS records

These were noted during planning; verify the exact record and locator before using.

| Topic | NTRS ID / reference | Status |
|---|---|---|
| ACME overview | 20210015913 | Verify |
| Saffire paper | 20170001636 | Verify |
| NASA SVS Saffire | 31394 | Verify |

---

## Citation format

In summaries and advisor answers:

```text
[S1] Saffire-I, PSI-98, Table 2.
```

In the UI:

- Citation chip → source title + link.
- Expander → retrieved passage + locator.
- Footer → full source list.

---

## Source quality checklist

- [ ] Primary source (PSI metadata, NTRS paper, NASA standard).
- [ ] Title and authors/years recorded.
- [ ] URL or DOI works.
- [ ] Locator is specific (table, figure, page).
- [ ] Units checked.
- [ ] Value type marked measured/reported/estimated.
- [ ] Confidence marked high/medium/low.
- [ ] License/credit recorded for images.
- [ ] No unverified number presented as fact.

---

## Notes

- Prefer NASA/partner primary sources over secondary summaries.
- Do not use a source you have not opened.
- If two sources disagree, show both and explain the difference.
- If a value is estimated from a figure, say so in the UI.
