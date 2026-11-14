"""Pull NASA PSI combustion metadata and build data/investigations.csv.

Source: PSI public JSON API (no key required).
Run:    .venv\\Scripts\\python.exe scripts\\fetch_psi.py
"""

from __future__ import annotations

import csv
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "psi_combustion.json"
OUT = ROOT / "data" / "investigations.csv"

API = (
    "https://psi.nasa.gov/geode-py/ws/repo/search"
    "?term=combustion&source=psi&type=investigation"
    "&sort=Public%20Release%20Date&order=desc&size=50"
)

# Hand-curated labels from the official challenge text and NASA fact sheets.
# Qualitative only: every numeric value belongs in test_conditions.csv with a locator.
CURATION = {
    "PSI-26": dict(
        id="bass", phase="prevention", facility="ISS / MSG",
        hardware="MSG flow duct", materials="Solid fuels: fabrics and plastics",
        key_finding="Solid-fuel ignition, spread and extinction were measured across flow and oxygen conditions in microgravity.",
        safety_implication="Solid-material flammability limits in low-g differ from 1-g tests; material selection needs low-g evidence.",
        limitations="Small samples in a glovebox; not a large-scale fire.",
    ),
    "PSI-25": dict(
        id="bass-ii", phase="prevention", facility="ISS / MSG",
        hardware="MSG flow duct", materials="Solid fuels: fabrics and plastics",
        key_finding="Extended BASS to additional fuels, geometries, flow speeds and oxygen concentrations.",
        safety_implication="Supports low-g flammability-limit data used to select materials for crew habitats.",
        limitations="Sample-scale; extrapolation to full habitat modules is not direct.",
    ),
    "PSI-98": dict(
        id="saffire-i", phase="prevention", facility="Cygnus (free-flying)",
        hardware="Saffire enclosure", materials="SIBAL fabric (cotton/fiberglass blend)",
        key_finding="A large-scale flame spread over fabric was measured in low gravity after Cygnus departure.",
        safety_implication="Provides the first large-sample low-g spread rates for spacecraft fire growth models.",
        limitations="Single material and limited number of tests.",
    ),
    "PSI-99": dict(
        id="saffire-ii", phase="prevention", facility="Cygnus (free-flying)",
        hardware="Saffire enclosure", materials="Multiple solid materials",
        key_finding="Extended large-scale low-g flammability testing to higher oxygen concentrations and more materials.",
        safety_implication="Bounds material flammability at elevated oxygen concentrations relevant to exploration atmospheres.",
        limitations="Cygnus cabin conditions, not a habitat interior.",
    ),
    "PSI-100": dict(
        id="saffire-iii", phase="prevention", facility="Cygnus (free-flying)",
        hardware="Saffire enclosure", materials="SIBAL fabric",
        key_finding="Tested how airflow velocity changes large-sample flame spread in low gravity.",
        safety_implication="Ventilation flow is a first-order control on fire growth in spacecraft.",
        limitations="Forced-flow conditions only.",
    ),
    "PSI-69": dict(
        id="flex", phase="suppression", facility="ISS / CIR",
        hardware="MDCA", materials="Liquid fuel droplets",
        key_finding="Quantified inert-gas (CO2, He) suppression and the limiting oxygen index for droplet flames.",
        safety_implication="Suppression by atmosphere dilution is viable, but the limiting oxygen index must be measured in low-g.",
        limitations="Droplet flames, not solid surfaces.",
    ),
    "PSI-68": dict(
        id="flex-2", phase="suppression", facility="ISS / CIR",
        hardware="MDCA", materials="Liquid fuel droplets",
        key_finding="Extended droplet extinction, soot and cool-flame measurements.",
        safety_implication="Informs suppression margins and the role of soot in detection.",
        limitations="Idealised droplet geometry.",
    ),
    "PSI-102": dict(
        id="same", phase="detection", facility="ISS / MSG",
        hardware="SAME / P-Trak", materials="Smoke from overheated spacecraft materials",
        key_finding="Measured smoke particle size distributions generated in low gravity.",
        safety_implication="Detector response depends on the source material; low-g smoke is not the same as terrestrial smoke.",
        limitations="Glovebox-scale smoke generation.",
    ),
    "PSI-101": dict(
        id="same-r", phase="detection", facility="ISS / MSG",
        hardware="SAME / P-Trak", materials="Smoke, including Pyrell",
        key_finding="Reflight confirmed particle sizes and added a fire-retardant material.",
        safety_implication="Supports selection and placement of spacecraft smoke detectors.",
        limitations="Limited material set.",
    ),
    "PSI-20": dict(
        id="acme-bre", phase="prevention", facility="ISS / CIR",
        hardware="ACME", materials="Gaseous fuels",
        key_finding="Burning-rate emulator reproduced solid-material burning behaviour with gaseous fuel flames.",
        safety_implication="Links material properties to flammability in still atmospheres.",
        limitations="Gaseous surrogate, not a burning solid.",
    ),
    "PSI-159": dict(
        id="acme-cfi-g", phase="prevention", facility="ISS / CIR",
        hardware="ACME", materials="Gaseous fuels: propane, n-butane, n-pentane",
        key_finding="Demonstrated steady cool diffusion flames over a wide range of dilution, flow and pressure.",
        safety_implication="Cool flames extend the range of conditions that can sustain combustion, including high-oxygen mixtures.",
        limitations="Gaseous fuels only; cool flames are weak but can transition to hot flames.",
    ),
    "PSI-107": dict(
        id="spice", phase="prevention", facility="ISS / MSG",
        hardware="MSG flow duct", materials="Gaseous fuels: methane, ethylene",
        key_finding="Measured smoke point and soot formation in coflow diffusion flames in low gravity.",
        safety_implication="Soot yield drives smoke-detector response and material selection.",
        limitations="Laminar jet flames, not real fires.",
    ),
    "PSI-21": dict(
        id="acme-cld-flame", phase="prevention", facility="ISS / CIR",
        hardware="ACME", materials="Gaseous fuels",
        key_finding="Measured coflow laminar diffusion flame structure and soot across dilution extremes.",
        safety_implication="Improves soot models used for detection and material screening.",
        limitations="Idealised laminar flames.",
    ),
    "PSI-22": dict(
        id="acme-e-field", phase="prevention", facility="ISS / CIR",
        hardware="ACME", materials="Gaseous fuels",
        key_finding="Used electric fields to study flame response as a partial-gravity analogue.",
        safety_implication="Constrains how intermediate gravity may change flammability where no partial-g data exist.",
        limitations="Electric-field analogy, not true partial gravity.",
    ),
    "PSI-23": dict(
        id="acme-s-flames", phase="prevention", facility="ISS / CIR",
        hardware="ACME", materials="Gaseous fuels",
        key_finding="Measured structure and response of spherical diffusion flames.",
        safety_implication="Provides fundamental data for flame models at low strain.",
        limitations="Spherical burner geometry.",
    ),
    "PSI-39": dict(
        id="cfi", phase="prevention", facility="ISS / CIR",
        hardware="MDCA", materials="Liquid fuels: n-dodecane, iso-dodecane mixtures",
        key_finding="Examined droplet cool-flame combustion over a wide pressure range.",
        safety_implication="Low-temperature chemistry can sustain reactions that simple ignition criteria miss.",
        limitations="Droplet geometry; pressures up to 5 atm.",
    ),
    "PSI-106": dict(
        id="slice", phase="prevention", facility="ISS / MSG",
        hardware="MSG flow duct", materials="Gaseous fuels: methane, ethylene",
        key_finding="Measured flame structure and liftoff of laminar diffusion flames in low gravity.",
        safety_implication="Improves models of flame stability near injectors and leaks.",
        limitations="Laminar jet flames.",
    ),
    "PSI-47": dict(
        id="daft", phase="detection", facility="ISS / MSG",
        hardware="TSI P-Trak", materials="Dust and aerosol particles",
        key_finding="Verified that a modified P-Trak particle counter works in microgravity.",
        safety_implication="Enabled SAME; also distinguishes dust from smoke, reducing nuisance alarms.",
        limitations="Feasibility test, not a fire test.",
    ),
    "PSI-10": dict(
        id="acme-flame-design", phase="prevention", facility="ISS / CIR",
        hardware="ACME", materials="Gaseous fuels",
        key_finding="Measured soot-inception limits for normal and inverse spherical diffusion flames.",
        safety_implication="Informs soot models and smoke-detector design.",
        limitations="Idealised burner.",
    ),
    "PSI-60": dict(
        id="ground-spice-analysis", phase="prevention", facility="Ground",
        hardware="—", materials="SPICE data (gaseous flames)",
        key_finding="Reanalysed SPICE images and soot models to explain 1-g versus 0-g soot differences.",
        safety_implication="Strengthens soot interpretation without new flight data.",
        limitations="Ground reanalysis, not a flight experiment.",
    ),
    "PSI-62": dict(
        id="ground-bass-modeling", phase="prevention", facility="Ground",
        hardware="—", materials="BASS data (solid fuels)",
        key_finding="Validated flamelet-generated-manifold models of concurrent spread against BASS.",
        safety_implication="Improves predictive models for spacecraft fire growth.",
        limitations="Modelling study.",
    ),
    "PSI-115": dict(
        id="ground-same-modeling", phase="detection", facility="Ground",
        hardware="—", materials="SAME data (smoke)",
        key_finding="Simulated smoke particle growth in 1-g and microgravity.",
        safety_implication="Supports detector sizing and alarm thresholds.",
        limitations="Modelling study.",
    ),
    "PSI-117": dict(
        id="ground-flex-coolflame-cfd", phase="suppression", facility="Ground",
        hardware="—", materials="FLEX data (droplets)",
        key_finding="CFD study of thermo-convective perturbation on cool-flame dynamics.",
        safety_implication="Explains when cool flames survive or extinguish.",
        limitations="Modelling study.",
    ),
    "PSI-142": dict(
        id="ground-flex-coolflame", phase="suppression", facility="Ground",
        hardware="—", materials="FLEX data (droplets)",
        key_finding="Counterflow-flame study of cool-flame transitions at extinction limits.",
        safety_implication="Improves extinction criteria used in suppression design.",
        limitations="Modelling/ground study.",
    ),
}


def get_source(rec: dict) -> str:
    src = (rec.get("Data Source Type") or "").strip()
    return src


def year(value: str) -> str:
    if not value:
        return ""
    for fmt in ("%m-%d-%Y", "%Y-%m-%d"):
        try:
            return str(datetime.strptime(value, fmt).year)
        except ValueError:
            continue
    m = re.search(r"(19|20)\d{2}", value)
    return m.group(0) if m else ""


def clean(text: str, limit: int = 600) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    return cut[: cut.rfind(" ")].rstrip(" ,;:") + " …"


def first_sentences(text: str, limit: int = 400) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = " ".join(parts[:2])
    return clean(out, limit)


def main() -> None:
    req = urllib.request.Request(API, headers={"User-Agent": "Mozilla/5.0 (flame-in-freefall)"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        payload = json.load(resp)

    hits = [h["_source"] for h in payload["hits"]["hits"]]
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    rows = []
    for rec in hits:
        accession = rec.get("Accession", "")
        meta = CURATION.get(accession)
        if not meta:
            continue
        acronym = rec.get("Acronym") or rec.get("Title", "")[:40]
        rows.append({
            "id": meta["id"],
            "name": rec.get("Title", ""),
            "short_name": acr_display(acronym, accession),
            "program": program_of(rec),
            "fire_safety_phase": meta["phase"],
            "facility": meta["facility"],
            "hardware_family": meta["hardware"],
            "year_start": year(rec.get("Investigation Start Date", "")),
            "year_end": year(rec.get("Investigation End Date", "")),
            "gravity": "microgravity" if rec.get("Project Type") == "Microgravity Investigation" else "1g",
            "objective": first_sentences(rec.get("Objectives", "")),
            "materials": meta["materials"],
            "sample_geometry": "",
            "o2_range_pct": "",
            "pressure_range_kpa": "",
            "flow_range_cm_s": "",
            "measured_variables": clean(rec.get("Approach", ""), 300),
            "key_finding": meta["key_finding"],
            "safety_implication": meta["safety_implication"],
            "limitations": meta["limitations"],
            "psi_id": accession,
            "psi_url": f"https://psi.nasa.gov/physci/repo/data/investigations/{accession}",
            "ntrs_url": "",
            "image_url": f"https://psi.nasa.gov/geode-py/ws/investigations/{accession}/image",
            "image_credit": "NASA / PSI",
            "data_volume": "",
            "confidence": "medium",
            "reviewed": "false",
            "notes": "Metadata-derived; numeric values not yet curated." if rec.get("Project Type") == "Microgravity Investigation" else "Ground study; related work, not flight data.",
        })

    rows.sort(key=lambda r: (r["gravity"] != "microgravity", r["fire_safety_phase"], r["id"]))

    fields = list(rows[0].keys())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"raw records: {len(hits)}")
    print(f"investigations written: {len(rows)} -> {OUT}")
    print(f"flight: {sum(1 for r in rows if r['gravity'] == 'microgravity')}, ground: {sum(1 for r in rows if r['gravity'] == '1g')}")


def acr_display(acronym: str, accession: str) -> str:
    ground = {
        "PSI-60": "SPICE analysis (ground)",
        "PSI-62": "BASS modeling (ground)",
        "PSI-115": "SAME utilization (ground)",
        "PSI-117": "Cool-flame CFD (ground)",
        "PSI-142": "Cool-flame transitions (ground)",
    }
    if accession in ground:
        return ground[accession]
    if not acronym:
        return accession
    return acronym.replace("ACME/", "ACME ").strip()


def program_of(rec: dict) -> str:
    acr = (rec.get("Acronym") or "").upper()
    if acr.startswith("ACME"):
        return "ACME"
    title = (rec.get("Title") or "").upper()
    if "SAFFIRE" in title or "SPACECRAFT FIRE" in title:
        return "Saffire"
    return "PSI"


if __name__ == "__main__":
    main()
