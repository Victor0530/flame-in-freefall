# PLAN — Flame in Freefall

> **Status:** Pre-hack planning only. Do not create project code, datasets, summaries, or assets before the event starts.
>
> **Challenge:** Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data
> **Event:** NASA Space Apps Challenge 2026 — local event, solo
> **Hackathon:** November 14–15, 2026
> **Resources release:** Friday, November 13, 2026
> **Local start:** _[confirm from local event schedule]_
> **Workspace:** `C:\Users\USER\Downloads\Nasa Space App Challenge 2026`

---

## 1. One-line pitch

An SI-powered dashboard that turns NASA's microgravity combustion data into evidence-ranked, cited fire-safety design rules for Moon and Mars habitats.

## 2. Non-negotiables

- **Strict compliance:** no project work before the official event start.
- **NASA/partner open data:** use PSI metadata, NTRS papers, and NASA standards.
- **Source every number:** table, figure, page, or DOI.
- **No raw mega-downloads:** do not plan around 11–33 GB PSI datasets.
- **Offline-safe demo:** the app must still work if Gemini is unavailable.
- **No overclaiming:** this is a decision-support prototype, not a certified fire-safety tool.

## 3. Scope

- **12 core investigations + 7 optional.**
- Cover all three fire-safety pillars: **prevention, detection, suppression**.
- Four tabs plus a mission-context sidebar.
- Local demo + Streamlit Community Cloud backup.

### Core 12

| # | Investigation | Pillar | Role in the app |
|---|---|---|---|
| 1 | BASS | Prevention | Solid-fuel spread baseline |
| 2 | BASS-II | Prevention | Extended solid-fuel conditions |
| 3 | Saffire-I | Prevention | Large-scale concurrent/opposed spread |
| 4 | Saffire-II | Prevention | Maximum oxygen concentration / flammability limits |
| 5 | Saffire-III | Prevention | Flow effects on large samples |
| 6 | FLEX | Suppression | CO₂/He extinguishment |
| 7 | FLEX-2 | Suppression | Droplet extinction |
| 8 | SAME | Detection | Smoke aerosol measurement |
| 9 | SAME-R | Detection | Refined smoke detection |
| 10 | ACME BRE | Prevention | Gaseous-fuel flammability |
| 11 | ACME CFI-G | Prevention | High-oxygen cool flames |
| 12 | SPICE | Prevention | Soot / smoke point |

### Optional 7

Add only if the core 12 are complete and sourced:

1. ACME CLD Flame
2. ACME E-FIELD Flames
3. ACME S-Flames
4. CFI
5. DAFT / DAFT-2
6. SLICE
7. Utilization of SAME Data (ground)

> Ground cool-flame studies can be added if time permits.

## 4. Architecture

### User flow

1. **Sidebar: Mission context** — destination, O₂ %, total pressure, material.
2. **Experiment Library** — browse, filter, inspect, select for comparison.
3. **Compare & Rank** — matched comparisons and evidence-priority ranking.
4. **Habitat Checker** — ppO₂, NASA-STD-6001 envelope, nearest evidence, design rules.
5. **Evidence Advisor** — cited Q&A, suggested questions, retrieved evidence.

### Stack

| Layer | Choice |
|---|---|
| UI | Streamlit 1.67 |
| Data | pandas 3.1 |
| Charts | Plotly 7.1 |
| Retrieval | scikit-learn TF-IDF |
| LLM | `google-genai` 3.0, Gemini 3.5 Flash-Lite default |
| PDF text | pypdf 7.0 |
| Deployment | Local + Streamlit Community Cloud |

### Data flow

```text
Official resources + PSI/NTRS metadata
        ↓
investigations.csv + test_conditions.csv + sources.json
        ↓
corpus/chunks.jsonl
        ↓
TF-IDF retrieval → top-5 chunks
        ↓
Gemini structured JSON → answer + citations + confidence + caveats
        ↓
qa_cache.json + st.cache_data + offline fallback
```

### AI rules

- One Gemini call per unique question.
- Structured JSON output: answer, key points, citations, confidence, caveats.
- Cache by question + retrieved chunk IDs.
- If no key or 429: serve cached answer or extractive fallback.
- Label AI-generated summaries as **AI-assisted, human-reviewed**.

## 5. Two-day schedule

### Day 1 — Saturday, November 14

| Time | Work |
|---|---|
| 09:00–09:45 | Finalize scope, init git repo, create folders, first commit |
| 09:45–12:30 | Curate 12 investigations + 25–30 test points; sources and confidence |
| 12:30–13:00 | Lunch |
| 13:00–15:30 | Build Library + Compare tabs |
| 15:30–18:00 | Build corpus, TF-IDF, Gemini client, summaries, Advisor, cache |
| 18:00–19:00 | Dinner |
| 19:00–21:00 | Build Habitat Checker + design rules |
| 21:00–23:00 | Integrate, offline mode, QA, commit |

### Day 2 — Sunday, November 15

| Time | Work |
|---|---|
| 09:00–10:30 | Content QA: numbers, units, citations, disclaimers |
| 10:30–12:00 | UI polish, empty/error states, accessibility |
| 12:00–13:00 | Demo script; rehearse |
| 13:00–14:30 | Record 2-minute video; screenshots |
| 14:30–16:00 | README, submission page, credits, links |
| 16:00–17:00 | Buffer; submit early |

> If the local event starts Friday evening, shift the first block to Friday and use Saturday morning for data QA.

## 6. Cut list if behind

| Priority | Cut |
|---|---|
| 1 | Free-form chatbot → cached Q&A + “Explain this view” |
| 2 | 12 investigations → 8 core |
| 3 | Images → icons |
| 4 | Optional 7 investigations |
| 5 | Similarity map → ranking table |
| 6 | Earth applications → one line |

**Keep:** Habitat Checker, citations, offline mode, source locators.

## 7. 90-second demo script

| Time | Beat |
|---|---|
| 0:00–0:15 | Problem: Moon base at 30%+ O₂ / ≤10.2 psi makes materials far more flammable; PSI data is hard to compare. |
| 0:15–0:35 | Select Moon base, 34% O₂, 70.3 kPa. Library filters to relevant prevention experiments. |
| 0:35–0:55 | Compare Saffire-I vs. BASS-II at matched conditions; show evidence-priority ranking and “why.” |
| 0:55–1:15 | Habitat Checker: ppO₂ ≈ 23.9 kPa, **outside NASA-STD-6001 Test 1 envelope**, risk HIGH; cite standard + Saffire. |
| 1:15–1:30 | Advisor answers “What should we test first?” with three cited bullets. |
| 1:30 | Close: evidence → interpretation → design rule. |

## 8. Judging map

| Criterion | Evidence |
|---|---|
| **Impact** | Moon/Mars habitat risk; design rules; Earth spin-offs; clear mission-engineer persona |
| **Creativity** | SI workflow: evidence ranking + habitat checker + cited advisor + “Explain this view” |
| **Technical validity** | Source locator per value; measured vs. estimated; uncertainty; NASA-STD-6001; partial-g caveat |
| **Relevance** | Summarize / rank / interpret; prevention / detection / suppression; PSI investigations |
| **Presentation** | Four-tab story; 90-second demo; before/after risk; clean visuals; video backup |

## 9. Definition of done

- [ ] 12 investigations curated with sources.
- [ ] 25–30 test points with `value_type` and `source_locator`.
- [ ] Four tabs working.
- [ ] Habitat Checker computes ppO₂ and flags >30% O₂.
- [ ] Advisor returns cited answers; 10+ cached Q&A.
- [ ] Offline mode tested.
- [ ] No secrets committed.
- [ ] README with data sources, limitations, and credits.
- [ ] 2-minute video recorded.
- [ ] Submission completed before the deadline.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Official resources differ from assumptions | Flexible ingestion; reconcile on Nov 13/14 |
| PSI raw data access/size | Use metadata, abstracts, papers; no mega-downloads |
| Gemini quota/429 | Cache, offline mode, quota guard |
| Unverified numbers | Source locator + confidence; omit if unverifiable |
| Time overrun | Cut list; protect Habitat Checker + citations |
| Deployment failure | Test local + cloud; record backup video |
| Rules concern | Git history from event start; no pre-work artifacts |
