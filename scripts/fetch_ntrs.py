"""Fetch NTRS abstracts for curated experiments and save them as corpus text.

Usage: python scripts/fetch_ntrs.py
Writes data/raw/ntrs/<id>.json and data/corpus/<id>.txt
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ntrs"
CORPUS = ROOT / "data" / "corpus"

QUERIES = {
    "saffire": "Saffire spacecraft fire safety experiment large scale flammability",
    "bass": "BASS burning and suppression of solids microgravity flame spread",
    "same": "smoke aerosol measurement experiment SAME International Space Station",
    "cfi-g": "gaseous coflow diffusion flames microgravity",
    "slice": "solid fuel ignition extinction",
    "flex": "flame extinguishment experiment FLEX droplet combustion International Space Station",
    "acme-bre": "Burning Rate Emulator",
    "standards": "JSC 29353",
}


def fetch(query: str, size: int = 4) -> list[dict]:
    url = (
        "https://ntrs.nasa.gov/api/citations/search?"
        + urllib.parse.urlencode({"q": query, "page.size": size})
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "flame-in-freefall/1.0"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            break
        except Exception as exc:  # transient network error
            last_error = exc
            if attempt == 2:
                raise
    else:  # pragma: no cover - loop always breaks or raises
        raise last_error or RuntimeError("NTRS request failed")

    out = []
    for item in data.get("results", []):
        out.append(
            {
                "id": str(item.get("id", "")),
                "title": item.get("title", ""),
                "abstract": item.get("abstract", ""),
                "publications": item.get("publications", []),
                "created": item.get("created", ""),
            }
        )
    return out


def _write_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    CORPUS.mkdir(parents=True, exist_ok=True)
    index = {}
    for slug, query in QUERIES.items():
        try:
            results = fetch(query)
        except Exception as exc:  # network is allowed to fail; report and continue
            print(f"[warn] {slug}: {exc}")
            continue
        index[slug] = results
        if not results:
            print(f"[warn] {slug}: no records, nothing written")
            continue
        (RAW / f"{slug}.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        lines = []
        for r in results:
            if not r["abstract"]:
                continue
            lines.append(f"# {r['title']}\nNTRS {r['id']}\n\n{r['abstract']}\n")
        _write_atomic(CORPUS / f"ntrs_{slug}.txt", "\n".join(lines))
        print(f"{slug}: {len(results)} records, {len(lines)} with abstracts")
    _write_atomic(RAW / "index.json", json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
