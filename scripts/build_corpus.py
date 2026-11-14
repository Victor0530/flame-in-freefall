"""Build the retrieval corpus for the Evidence Advisor.

Sources, in order of authority:
1. Curated test-condition rows (quoted from NASA documents).
2. PSI investigation records (objectives, findings, limitations).
3. NTRS abstracts fetched by scripts/fetch_ntrs.py.
4. The 2015 Researcher's Guide to Combustion Science (NASA NP-2015-10-034-JSC).
5. Short, quoted passages from NASA-STD-6001B and JSC 29353.

Writes data/corpus/chunks.jsonl — one JSON object per passage.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CORPUS = DATA / "corpus"

STANDARDS = [
    {
        "id": "std-6001b-test1",
        "text": (
            "NASA-STD-6001B Test 1 evaluates upward flame propagation in a normal-gravity environment "
            "at 30 percent oxygen and 10.2 psia (70.3 kPa), giving an oxygen partial pressure of about "
            "21.1 kPa. The test is a screening test: it is conducted in 1 g, so a pass does not "
            "establish low-gravity flammability limits."
        ),
        "source_label": "NASA-STD-6001B (Test 1)",
        "url": "https://standards.nasa.gov/standard/NASA/NASA-STD-6001",
        "locator": "Test 1, configuration and test conditions",
        "kind": "standard",
    },
    {
        "id": "std-exploration-atmosphere",
        "text": (
            "A NASA exploration atmosphere under study is 34 percent oxygen at 8.2 psia (56.5 kPa), "
            "which gives an oxygen partial pressure of about 19.2 kPa. This is below the 21.1 kPa of "
            "the historical Test 1 point, but the oxygen concentration is higher, and low-gravity "
            "flammability limits differ from 1-g limits."
        ),
        "source_label": "Exploration atmosphere (NTRS 20220009546)",
        "url": "https://ntrs.nasa.gov/citations/20220009546",
        "locator": "Exploration atmosphere definition",
        "kind": "standard",
    },
    {
        "id": "jsc-29353",
        "text": (
            "JSC 29353, Flammability Configuration Analysis for Spacecraft Applications, defines the "
            "analysis method used to show that a spacecraft configuration meets flammability "
            "requirements. It complements NASA-STD-6001 material screening by addressing configuration, "
            "geometry, and applied environments rather than a single material coupon."
        ),
        "source_label": "JSC 29353 rev D (2024)",
        "url": "https://standards.nasa.gov/standard/JSC/JSC-29353",
        "locator": "Scope",
        "kind": "standard",
    },
    {
        "id": "sma-apollo-1",
        "text": (
            "The Apollo 1 fire in a 100 percent oxygen atmosphere at about 16.7 psia spread in seconds "
            "through combustible materials in the crew cabin, and the crew could not open the inward-"
            "opening hatch. The accident drove changes to materials selection, hatch design, and the "
            "use of lower-pressure oxygen atmospheres."
        ),
        "source_label": "NASA SMA — Apollo 1",
        "url": "https://sma.nasa.gov/sma-disciplines/accllp/apollo-1",
        "locator": "Accident summary",
        "kind": "history",
    },
    {
        "id": "history-mir-fire",
        "text": (
            "In February 1997 a fire broke out on the Mir space station from a defective oxygen-generating "
            "cartridge. Crew used a handheld extinguisher, and the fire was limited by the absence of "
            "buoyant flow: smoke spread through the station and detection was delayed."
        ),
        "source_label": "NASA history — Mir fire, 25 years later",
        "url": "https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/",
        "locator": "Fire timeline",
        "kind": "history",
    },
]


def clean(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_long(text: str, size: int = 1100) -> list[str]:
    if len(text) <= size:
        return [text] if text else []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, buf = [], ""
    for s in sentences:
        if len(buf) + len(s) + 1 > size and buf:
            chunks.append(buf.strip())
            buf = s
        else:
            buf = f"{buf} {s}".strip()
    if buf:
        chunks.append(buf.strip())
    return chunks


def investigation_docs() -> list[dict]:
    docs = []
    path = DATA / "investigations.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            body = " ".join(
                filter(
                    None,
                    [
                        f"{row['name']} ({row['short_name']}) is a {row['gravity']} "
                        f"{row['fire_safety_phase']} investigation.",
                        f"Objective: {row['objective']}",
                        f"Materials: {row['materials']}.",
                        f"Measured variables: {row['measured_variables']}.",
                        f"Key finding: {row['key_finding']}",
                        f"Safety implication: {row['safety_implication']}",
                        f"Limitations: {row['limitations']}",
                        f"Facility: {row['facility']}.",
                    ],
                )
            )
            docs.append(
                {
                    "id": f"psi-{row['psi_id']}",
                    "text": clean(body),
                    "source_label": f"PSI record {row['psi_id']} — {row['short_name']}",
                    "url": row["psi_url"] or "https://psi.nasa.gov/",
                    "locator": "Objectives / Approach",
                    "kind": "psidata",
                }
            )
    return docs


def condition_docs() -> list[dict]:
    docs = []
    path = DATA / "test_conditions.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["point_type"] == "qualitative":
                continue
            bits = [f"{row['short_name']} condition: {row['point_label']}."]
            if row["o2_pct"]:
                bits.append(f"Oxygen {row['o2_pct']} percent.")
            if row["pressure_kpa"]:
                bits.append(f"Pressure {row['pressure_kpa']} kPa.")
            if row["flow_cm_s"]:
                bits.append(f"Forced flow {row['flow_cm_s']} cm/s.")
            if row["material"]:
                bits.append(f"Material: {row['material']}.")
            if row["source_quote"]:
                bits.append(f'Source states: "{row["source_quote"]}"')
            docs.append(
                {
                    "id": f"cond-{row['investigation_id']}-{row['point_label'][:24]}",
                    "text": clean(" ".join(bits)),
                    "source_label": f"{row['source_locator']} — {row['short_name']}",
                    "url": row["source_url"],
                    "locator": row["source_locator"],
                    "kind": "condition",
                }
            )
    return docs


def ntrs_docs() -> list[dict]:
    docs = []
    for path in sorted((DATA / "raw" / "ntrs").glob("*.json")):
        if path.name == "index.json":
            continue
        for item in json.loads(path.read_text(encoding="utf-8")):
            abstract = clean(item.get("abstract", ""))
            if len(abstract) < 200:
                continue
            for i, chunk in enumerate(split_long(abstract)):
                docs.append(
                    {
                        "id": f"ntrs-{item['id']}-{i}",
                        "text": chunk,
                        "source_label": f"NTRS {item['id']} — {item['title'][:90]}",
                        "url": f"https://ntrs.nasa.gov/citations/{item['id']}",
                        "locator": "Abstract",
                        "kind": "ntrs",
                    }
                )
    return docs


def guide_docs() -> list[dict]:
    path = DATA / "raw" / "researchers_guide_2015.pdf"
    if not path.exists():
        return []
    docs = []
    reader = PdfReader(str(path))
    for page_no, page in enumerate(reader.pages, start=1):
        text = clean(page.extract_text() or "")
        if len(text) < 200:
            continue
        for i, chunk in enumerate(split_long(text)):
            docs.append(
                {
                    "id": f"guide-p{page_no}-{i}",
                    "text": chunk,
                    "source_label": "Researcher's Guide to Combustion Science (NASA NP-2015-10-034-JSC)",
                    "url": "https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/",
                    "locator": f"PDF page {page_no}",
                    "kind": "guide",
                }
            )
    return docs


def main() -> None:
    CORPUS.mkdir(parents=True, exist_ok=True)
    docs = []
    for builder in (condition_docs, investigation_docs, ntrs_docs, guide_docs):
        part = builder()
        print(f"{builder.__name__}: {len(part)} passages")
        docs.extend(part)
    docs.extend(STANDARDS)
    for doc in docs:
        doc["text"] = clean(doc["text"])
    out = CORPUS / "chunks.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for doc in docs:
            fh.write(json.dumps(doc, ensure_ascii=False) + "\n")
    words = sum(len(d["text"].split()) for d in docs)
    print(f"wrote {len(docs)} passages, {words:,} words -> {out}")


if __name__ == "__main__":
    main()
