# SUBMISSION — Flame in Freefall

> Submit early. Keep a backup ZIP of the code and video.
>
> **Deadline:** _[confirm local event deadline]_

---

## 1. Submission checklist

### Project page

- [ ] Project title.
- [ ] One-sentence tagline.
- [ ] Challenge selected.
- [ ] Team members (solo).
- [ ] Short description.
- [ ] How it works.
- [ ] Data and sources.
- [ ] Technical approach.
- [ ] Limitations and caveats.
- [ ] What is next.
- [ ] Built with.
- [ ] Credits.
- [ ] Repo URL.
- [ ] Demo URL.
- [ ] Video URL.
- [ ] Screenshots.

### Repository

- [ ] Public or judge-accessible.
- [ ] `README.md` complete.
- [ ] `requirements.txt` pinned.
- [ ] `.gitignore` excludes `.venv/`, `.env`, `.streamlit/secrets.toml`.
- [ ] No API keys or secrets committed.
- [ ] Fresh clone installs and runs.
- [ ] Data files and sources included.
- [ ] License/credits for images and data.
- [ ] Commit history starts at the event.

### Demo

- [ ] Local app runs.
- [ ] Streamlit Cloud app runs.
- [ ] Offline mode works.
- [ ] 90-second live demo rehearsed.
- [ ] 2-minute video recorded and uploaded.
- [ ] Backup video saved locally.

### Final checks

- [ ] Every number has a source locator.
- [ ] Units are consistent.
- [ ] NASA-STD-6001 and >30% O₂ statement checked.
- [ ] Partial-gravity caveat present.
- [ ] Prototype disclaimer present.
- [ ] AI assistance disclosed.
- [ ] No NASA endorsement implied.
- [ ] All links tested.
- [ ] Submission completed before the deadline.

---

## 2. Project page fields

### Title

**Flame in Freefall — [your subtitle]**

### Tagline

Turning microgravity combustion data into cited fire-safety design rules for Moon and Mars habitats.

### Short description

A Streamlit dashboard that summarizes, compares, ranks, and interprets NASA's microgravity combustion investigations. It combines a mission-context sidebar, an evidence library, matched comparisons, a ppO₂-aware Habitat Checker, and a cited AI advisor.

### How it works

1. Curated investigation and test-condition data from PSI/NTRS.
2. Evidence-priority ranking with transparent weights.
3. Habitat Checker computes ppO₂ and checks NASA-STD-6001 envelopes.
4. TF-IDF retrieval + Gemini structured answers with citations.
5. Offline cache for demo reliability.

### Data and sources

List PSI IDs, NTRS papers, NASA standards, and image credits. Link to `SOURCES.md`.

### Limitations

- Prototype, not certified fire-safety guidance.
- No partial-gravity data in PSI; lunar/Mars extrapolation is bounded, not measured.
- Some values are estimated from figures and marked as such.
- Ranking weights are expert-defined, not NASA-endorsed.
- AI answers are grounded in retrieved sources but should be reviewed.

### What is next

- Add optional investigations.
- Expand test-condition extraction.
- Add partial-gravity data when LUCI/FM2 are available.
- Validate with fire-safety engineers.

---

## 3. Two-minute video outline

| Time | Content |
|---|---|
| 0:00–0:15 | Problem: fire safety in Moon/Mars habitats; PSI data is hard to compare. |
| 0:15–0:35 | Solution: SI-powered evidence dashboard; four tabs. |
| 0:35–1:15 | Demo: mission context → library → compare/rank → habitat checker → advisor. |
| 1:15–1:35 | Technical validity: sources, confidence, ppO₂, NASA-STD-6001, partial-g caveat. |
| 1:35–1:50 | Impact: design rules, Earth spin-offs. |
| 1:50–2:00 | Close: evidence → interpretation → safer missions. |

---

## 4. Credits and compliance

- **NASA data:** PSI, NTRS, NASA standards; link each source.
- **Images:** NASA image URLs and credit lines; do not imply endorsement.
- **AI:** disclose Gemini usage; label AI-assisted summaries.
- **License:** choose a permissive license for your code (e.g. MIT) unless the event says otherwise.
- **Rules:** git history from event start; no pre-work artifacts.

---

## 5. Judging map

| Criterion | Where to point |
|---|---|
| **Impact** | Moon/Mars habitat risk, design rules, Earth spin-offs |
| **Creativity** | SI workflow, evidence ranking, Habitat Checker, cited advisor |
| **Technical validity** | Source locators, confidence, ppO₂, NASA-STD-6001, partial-g caveat |
| **Relevance** | Summarize/rank/interpret; prevention/detection/suppression; PSI investigations |
| **Presentation** | Four-tab story, 90-second demo, clean visuals, video backup |
