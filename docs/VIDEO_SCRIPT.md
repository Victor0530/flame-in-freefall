# Demo video script — captions only

Target: **2:00**, 1080p, no voiceover. All narration is burned-in captions.
Record the running app at 1440×900 (browser zoom 100%), then crop to 16:9.

## Shot list and captions

| Time | On screen | Caption text |
|---|---|---|
| 0:00–0:08 | Title card: "🔥 Flame in Freefall" on the app background | A fire in a Moon habitat gives a crew minutes, not hours. |
| 0:08–0:18 | Library tab, scroll cards slowly | The evidence to prevent it exists, spread across decades of microgravity combustion experiments. |
| 0:18–0:28 | Library filters: pillar, search, material focus | Flame in Freefall turns NASA's 24 public investigations into searchable, cited evidence. |
| 0:28–0:38 | Hover a card: key finding + safety implication | Each record carries its key finding, its safety implication, and its limits. |
| 0:38–0:50 | Compare tab: preset, target line | Ask a hard question: which evidence applies to a 34% oxygen, 8.2 psia cabin? |
| 0:50–1:02 | Ranking table: ACME BRE #1, coverage 100 | The ranker scores atmosphere match, gravity, flow, diagnostics and recency. |
| 1:02–1:12 | Expand "How the score is calculated", move weights | Missing data lowers coverage. It is never replaced by an assumption. |
| 1:12–1:22 | Condition matrix with quotes | Every numeric cell is copied from quoted NASA text, with its locator. |
| 1:22–1:36 | Habitat Checker: gauge, 19.2 kPa | The Habitat Checker converts any cabin to oxygen partial pressure. |
| 1:36–1:46 | Test 1 metric, warning block | NASA-STD-6001B Test 1 was 30% oxygen at 70.3 kPa — 21.1 kPa ppO₂. |
| 1:46–1:56 | Design rules list | Saffire and BASS show why a 1-g pass is not a low-gravity clearance. |
| 1:56–2:04 | Advisor: ask "What should a Moon habitat test first?" | Ask the advisor and get an answer with passage-level citations. |
| 2:04–2:14 | Answer with [S1]…[S5] and source list | Reviewed answers are checked in advance. Generated answers are grounded and labelled. |
| 2:14–2:24 | Ask "Can acrylic burn at 30% oxygen?" | When NASA has no data, the advisor says so instead of guessing. |
| 2:24–2:34 | Footer: Data / Method / Limits | Decision support, not certification — and every limit is stated up front. |
| 2:34–2:45 | Title card + repo URL | Flame in Freefall. Evidence, not guesswork. |

Adjust timings after recording; the content order matters more than the seconds.

## Recording steps

1. Start the app: `streamlit run app.py`.
2. Set the window to 1440×900; hide the browser toolbar so only the app is captured.
3. Record segments separately (one per row above) — easier to fix a bad take.
4. Add captions in CapCut / DaVinci Resolve / ffmpeg. Keep one caption line at a time.
5. Export 1080p MP4, under 200 MB.
6. Upload to YouTube as **Unlisted**; keep the link for the submission page.
7. Save a local backup copy (`docs/demo.mp4` or an external drive).

## Burn-in with ffmpeg (optional)

```bash
ffmpeg -i raw.mp4 -vf "subtitles=captions.srt:force_style='FontName=Inter,FontSize=20,PrimaryColour=&HFFFFFF&,BorderStyle=3,Outline=0,Shadow=0,BackColour=&H80000000&'" -c:a copy demo.mp4
```

`captions.srt` uses the same text as the table above, one cue per row.

## Narration-free rules

- No claims about "safe" materials.
- Always say "microgravity evidence", not "proven in space" for ground studies.
- Show the coverage column when showing a rank.
- Do not show API keys, terminal history, or `.streamlit/secrets.toml`.
