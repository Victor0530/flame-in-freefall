# 🔥 Flame in Freefall

**Microgravity combustion data, turned into evidence-ranked fire-safety decisions for Moon and Mars habitats.**

Built for the [NASA Space Apps Challenge 2026](https://www.spaceappschallenge.org/) challenge
*"Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data."*

Every claim in the app carries a source locator, and where NASA has not published a number,
the app says so instead of guessing.

---

## The problem

A habitat fire is one of the few failures in spaceflight that can kill a crew within minutes.
NASA has run combustion experiments in microgravity for decades — BASS, FLEX, Saffire, ACME,
SAME, CFI — but the evidence is spread across the Physical Sciences Informatics (PSI) repository,
NTRS papers, standards documents, and programme fact sheets. A habitat designer cannot compare
those results at a glance, and the public records often omit the numeric test conditions entirely.

That gap is the real risk: a material that passes a 1-g upward-propagation test at 30% oxygen
has **not** been shown to behave the same way in low gravity, at a different pressure, or under
the ventilation conditions of a spacecraft cabin.

## What the app does

![Experiment library](docs/screenshots/library.png)

Four linked views, one evidence base:

| Tab | Question it answers |
|---|---|
| 📚 **Library** | What did NASA actually test, and what did each experiment conclude? |
| ⚖️ **Compare & Rank** | Which investigations best support a decision at *my* atmosphere, and how complete is that evidence? |
| 🛡️ **Habitat Checker** | What is my oxygen partial pressure, how does it compare with NASA-STD-6001B Test 1, and what should I test first? |
| 💬 **Advisor** | Ask a fire-safety question and get an answer with passage-level citations — or an explicit "not in the evidence base." |

### Library

All 24 public PSI combustion investigations (19 flight, 5 ground/modelling), tagged by the
fire-safety pillar they inform — **prevention**, **detection**, or **suppression** — with key
finding, safety implication, materials, measured variables, and limitations on every card.

### Compare & Rank

A transparent, user-adjustable score over five documented dimensions:

| Dimension | Default weight | What it measures |
|---|---|---|
| Atmosphere match | 0.45 | Did the experiment run at, or span, the target O₂ fraction and pressure? |
| Microgravity evidence | 0.30 | Flight data, partial gravity, or ground only? |
| Flow characterisation | 0.10 | Is the forced-flow condition quantified? |
| Diagnostics breadth | 0.10 | How many measured variables are documented? |
| Recency | 0.05 | How current is the programme? |

Missing dimensions are **dropped** and reported as reduced *coverage* — never filled with an
assumed value. At the exploration atmosphere (34% O₂ / 56.5 kPa), ACME BRE ranks first because
its published test matrix includes that exact point, not because it is "safer."

![Compare and rank](docs/screenshots/compare.png)

### Habitat Checker

Computes ppO₂ from O₂ fraction and total pressure, plots it against the historical
NASA-STD-6001B Test 1 limit (30% O₂ at 70.3 kPa → 21.1 kPa ppO₂), and shows the exploration
atmosphere (34% O₂ at 56.5 kPa → 19.2 kPa ppO₂). It then derives design rules from the flight
evidence: ventilation changes spread and extinction, smoke particle sizes differ in low gravity,
and suppression margins are not established by 1-g testing.

![Habitat checker](docs/screenshots/habitat.png)

### Advisor

Hybrid retrieval (Gemini embeddings + TF-IDF fallback) over 198 curated passages from PSI records,
NTRS abstracts, the 2015 *Researcher's Guide to Combustion Science*, and standards/history
documents. Answers are either **human-reviewed** (the six suggested questions) or **grounded
generation** with `[S#]` citations back to the retrieved passage. With no API key it degrades to
extractive quoting, and previously answered questions are cached.

![Evidence advisor](docs/screenshots/advisor.png)

## Data and provenance

| Source | Use | Access |
|---|---|---|
| [PSI repository](https://psi.nasa.gov/physci/repo/search?q=combustion&data_source=psi&data_type=investigation) | 24 investigations, metadata, objectives, findings | Public JSON API |
| [NTRS](https://ntrs.nasa.gov/) | Abstracts and full text for Saffire, BASS, FLEX, SAME, CFI, SLICE, ACME | Public API |
| [NASA-STD-6001B](https://standards.nasa.gov/standard/NASA/NASA-STD-6001) | Flammability, offgassing, compatibility requirements; Test 1 envelope | Public standard |
| [JSC 29353](https://standards.nasa.gov/standard/JSC/JSC-29353) | Flammability configuration analysis | Public standard |
| [Researcher's Guide to Combustion Science (2015)](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/) | Experiment background and apparatus | NASA PDF |
| [NASA Combustion Science](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/) | Programme context | NASA page |
| Apollo 1, Apollo 13, Mir fire, NASA spin-offs | Prevention/detection/suppression lessons and Earth applications | NASA history |

**Condition curation policy.** Every number in `data/test_conditions.csv` is quoted from source
text with a locator. Blank means *not published*, never zero. Where a record only describes
conditions qualitatively, the row is marked `qualitative` and excluded from numeric scoring.
26 rows are curated; 8 investigations have at least one numeric condition.

Known gaps are documented openly: Saffire-III's public record states a 30 cm/s flow but not its
oxygen concentration; Saffire-II's objectives do not claim a higher-oxygen test; most ACME
investigations publish no numeric matrix. The app shows those gaps rather than filling them.

## Architecture

```
PSI JSON API ─┐
NTRS API ─────┼─► scripts/fetch_psi.py ──► data/investigations.csv ─┐
NASA PDFs ────┘   scripts/fetch_ntrs.py                            ├─► Streamlit app
                  scripts/extract_pdfs.py ─► data/corpus/*.txt     │   app.py
                  data/test_conditions.csv (hand-curated, quoted)  │   ├─ tabs/library.py
                                                                   │   ├─ tabs/compare.py   ◄─ lib/scoring.py
                  scripts/build_corpus.py ─► chunks.jsonl (198)    │   ├─ tabs/habitat.py
                  scripts/build_embeddings.py ─► embeddings.npz    │   └─ tabs/advisor.py   ◄─ lib/advisor.py
                                                                   └─ data/faq.json (reviewed answers)
```

The app reads CSVs at runtime. Rebuilding the corpus or embeddings is only needed to change the
advisor's knowledge base.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
streamlit run app.py
```

The app runs without any key. To enable grounded Gemini answers, create
`.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-key"
```

Use `gemini-3.5-flash-lite` for generation and `gemini-embedding-001` for embeddings.

## Rebuild the data

```bash
python scripts/fetch_psi.py          # PSI search API → investigations.csv
python scripts/fetch_ntrs.py         # NTRS abstracts → data/raw/ntrs
python scripts/extract_pdfs.py       # Researcher's Guide + programme page → corpus text
python scripts/build_corpus.py       # chunk → data/corpus/chunks.jsonl
python scripts/build_embeddings.py   # embed → embeddings.npz + query cache
```

## Tests

```bash
python -m pytest -q                  # smoke tests for data integrity and ranking
python -m streamlit run app.py       # manual check of all four tabs
```

`tests/test_smoke.py` verifies the curated data contract: 24 records, required columns present,
every numeric condition has a source quote, and ranking is deterministic and coverage-aware.

## Limits

- **Decision support, not certification.** The app does not approve materials or configurations.
- **No partial-gravity flight data.** Lunar and Martian gravity are bounded by argument, not measured.
- **1-g screening is not conservative for low gravity.** NASA-STD-6001B Test 1 is a 1-g upward
  propagation test; Saffire and BASS show flow and gravity change the outcome.
- **Public metadata is incomplete.** Absence of a published condition is shown as zero coverage,
  not as an absence of hazard.
- **Ranking weights are expert-defined** and adjustable in the UI; they are not NASA-endorsed.
- **AI answers require review.** They are grounded in retrieved passages but can still misread them.

## Earth applications

The same evidence supports terrestrial fire safety: NASA-derived air tanks, ionization/optical
smoke detectors, and fire-resistant attire are direct spin-offs of crewed-spaceflight fire
research. Materials screening, low-ventilation fire behaviour, and detector selection transfer
to aircraft, submarines, clean rooms, and high-rise compartments.

## Repository layout

```
app.py                     Streamlit entry point, sidebar, hero, footer
lib/data.py                Cached data access, constants, presets, material matching
lib/scoring.py             Transparent evidence ranking
lib/advisor.py             Retrieval, grounding, caching, offline fallback
lib/theme.py               CSS and hero component
tabs/library.py            Experiment library
tabs/compare.py            Compare & rank, condition matrix
tabs/habitat.py            ppO₂ checker, design rules
tabs/advisor.py            Advisor UI
scripts/                   Data acquisition and corpus build
data/                      Curated CSVs, corpus, embeddings, cache, reviewed answers
docs/                      Screenshots and demo script
tests/                     Data-contract and ranking tests
```

## Credits and disclosure

- Data and imagery: NASA (PSI, NTRS, NASA standards). NASA does not endorse this project.
- AI assistance: code and documentation were developed with an AI coding assistant; AI-generated
  answers in the app are labelled and grounded in retrieved NASA text.
- Standards values are quoted from public NASA documents; verify against the current revision
  before any engineering use.

MIT licensed — see [LICENSE](LICENSE).
