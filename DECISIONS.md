# DECISIONS — Flame in Freefall

> Record decisions that affect scope, architecture, data, or presentation. Add new entries during the event; do not rewrite history.
>
> **Status:** Proposed · Accepted · Superseded · Revisit

---

## Decision log

| ID | Date | Decision | Rationale | Alternatives considered | Status |
|---|---|---|---|---|---|
| D1 | 2026-11-09 | Comply strictly with the rules; no project work before the official event start | Official FAQ and 2026 page prohibit starting before the hackathon | Pre-build and risk disqualification | Accepted |
| D2 | 2026-11-09 | Participate in the local event, solo | Local events allow 1–6 participants; solo is valid | Universal Event requires 2+ | Accepted |
| D3 | 2026-11-09 | Local demo + Streamlit Community Cloud backup | Reliability; cloud link is useful for submission | Local only; other hosting | Accepted |
| D4 | 2026-11-09 | 12 core investigations + 7 optional | Finishable in two days; covers prevention/detection/suppression | All 19 in depth; 8 core only | Accepted |
| D5 | 2026-11-09 | Use Streamlit, not React | Fastest path to a working dashboard; prior experience | React + FastAPI | Accepted |
| D6 | 2026-11-09 | Use TF-IDF retrieval, not FAISS + sentence-transformers | Small corpus; fewer dependencies; reliable deployment | FAISS + local embeddings | Accepted |
| D7 | 2026-11-09 | Default to `gemini-3.5-flash-lite`; fallback `gemini-3.8-flash` | Free-tier capable; current models; configurable | `gemini-2.0-flash` (shut down); `gemini-2.5-flash` (deprecated) | Accepted |
| D8 | 2026-11-09 | Four tabs + mission-context sidebar | Coherent mission-engineer workflow | Library-first; chatbot-first | Accepted |
| D9 | 2026-11-09 | Two-table data model: `investigations.csv` + `test_conditions.csv` | Separates investigation facts from test measurements | Single `experiments.csv` | Accepted |
| D10 | 2026-11-09 | Habitat Checker computes ppO₂ and checks NASA-STD-6001 | O₂ percentage alone is insufficient; total pressure matters | Simple O₂-only risk score | Accepted |
| D11 | 2026-11-09 | No raw 11–33 GB PSI downloads | Time, bandwidth, access risk | Download and process raw data | Accepted |
| D12 | 2026-11-09 | Require `value_type`, `source_locator`, `confidence` for numeric values | Technical validity; avoids unverifiable claims | Trust secondary summaries | Accepted |
| D13 | 2026-11-09 | Generate summaries, corpus, and cache only during the event | Avoid pre-work; keep git history clean | Pre-generate before event | Accepted |
| D14 | 2026-11-09 | Initialize the git repo at the event start | Evidence of compliance and work timeline | Init earlier | Accepted |
| D15 | 2026-11-14 | Official resource set accepted; PSI is the only dataset, NASA-STD-6001B and JSC 29353D used as supporting standards | Resources provide context/history/spin-offs, not curated data; standards are public but not challenge-provided | Treating R2/R4 as optional; skipping standards | Accepted |
| D16 | 2026-11-14 | Ingest PSI via its public JSON API (`/geode-py/ws/repo/...`), not HTML scraping | Structured metadata for all 24 combustion records; reproducible; no key | Manual entry; browser scraping | Accepted |
| D17 | 2026-11-14 | Use 34% O₂ / 56.5 kPa as the Moon/Mars preset; compare against NASA-STD-6001B's 30% / 70.3 kPa Test 1 point; no binary compliance claim | 34% / 70.3 kPa is not a NASA design point; Test 1 is 1-g and not conservative for low-g | Keeping 34% / 70.3 kPa; simple O₂-only score | Accepted |
| D18 | 2026-11-14 | Library ships all 19 flight investigations from API metadata; hand-curate test conditions only for the core 12 | Metadata is free and strengthens coverage; extraction time stays bounded | Core 12 only; all 24 in depth | Accepted |
| D19 | 2026-11-14 | Build corpus from NTRS abstract/fulltext `.txt` + PSI objectives + R4, not PSI raw data | Small, citable, fast; avoids 11–33 GB downloads | Raw PSI data processing | Accepted |

---

## Open questions

| # | Question | Needed by | Owner | Answer |
|---|---|---|---|---|
| 1 | Exact local event start time | Nov 13 | You | Event live; submission window Sat 09:00 → Sun 23:59 local |
| 2 | Does the local event start Friday evening? | Nov 13 | You | No — Saturday |
| 3 | Are the official resources mandatory or suggested? | Nov 13 | You | Suggested; no mandatory files or API keys |
| 4 | Does the official resource set change the 12 core list? | Nov 13 | You | No — all 12 exist; add PSI-10 and PSI-47 as optional |
| 5 | Is there a small curated data file, or only large PSI datasets? | Nov 13 | You | No dataset; PSI JSON API + per-investigation reports are the usable layer |

---

## New decision template

```markdown
### D__ — [short title]

- **Date:**
- **Decision:**
- **Why:**
- **Alternatives:**
- **Consequences:**
- **Status:** Proposed / Accepted / Superseded / Revisit
```
