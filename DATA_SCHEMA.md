# DATA SCHEMA — Flame in Freefall

> **Template only.** Do not populate challenge data before the event starts. This file defines the structure, units, and provenance rules so curation is fast and consistent.
>
> **Principle:** separate *investigation-level* facts from *test-condition-level* measurements.

---

## 1. Two tables, two levels

| File | Grain | Purpose |
|---|---|---|
| `data/investigations.csv` | One row per investigation | Objectives, materials, facility, ranges, key finding, safety implication |
| `data/test_conditions.csv` | One row per test point | Actual measured/reported conditions and outcomes used in charts |
| `data/sources.json` | One entry per source | URLs, DOIs, PSI IDs, locators, confidence |

Never mix an investigation summary with a single test measurement in the same row.

---

## 2. `investigations.csv`

### Identity

| Column | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Lowercase slug, e.g. `saffire-i` |
| `name` | string | yes | Full investigation name |
| `short_name` | string | yes | Display name, e.g. `Saffire-I` |
| `program` | string | no | ACME, PSI, etc. |
| `fire_safety_phase` | enum | yes | `prevention`, `detection`, `suppression` |
| `facility` | string | no | ISS, MSG, CIR, MDCA, etc. |
| `hardware_family` | string | no | ACME modular, MDCA, MSG flow duct, Saffire |
| `year_start` | integer | no | Start year |
| `year_end` | integer | no | End year |
| `gravity` | string | yes | `microgravity`, `1g`, `partial-g`, `mixed` |

### Science

| Column | Type | Required | Description |
|---|---|---|---|
| `objective` | text | yes | 1–2 sentence objective |
| `materials` | string | yes | Fuels/materials tested |
| `sample_geometry` | string | no | Shape and size |
| `o2_range_pct` | string | no | Range, e.g. `21–22` |
| `pressure_range_kpa` | string | no | Range in kPa |
| `flow_range_cm_s` | string | no | Range in cm/s |
| `measured_variables` | string | no | Sensors / measurements |
| `key_finding` | text | yes | 1–2 sentence result |
| `safety_implication` | text | yes | What it means for fire safety |
| `limitations` | text | no | Caveats and gaps |

### Provenance

| Column | Type | Required | Description |
|---|---|---|---|
| `psi_id` | string | no | e.g. `PSI-98` |
| `psi_url` | string | no | PSI page URL |
| `ntrs_url` | string | no | NTRS paper URL or DOI |
| `image_url` | string | no | NASA image URL |
| `image_credit` | string | no | Credit line |
| `data_volume` | string | no | e.g. `11.41 GB` |
| `confidence` | enum | yes | `high`, `medium`, `low` |
| `reviewed` | boolean | yes | Human review completed |
| `notes` | text | no | Anything else |

---

## 3. `test_conditions.csv`

| Column | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique test ID, e.g. `saffire-i-t01` |
| `investigation_id` | string | yes | Must match `investigations.id` |
| `material` | string | yes | Material/fuel |
| `sample_size` | string | no | Dimensions |
| `o2_pct` | float | yes | Oxygen concentration, % |
| `pressure_kpa` | float | yes | Total pressure, kPa |
| `ppO2_kpa` | float | computed | `o2_pct / 100 * pressure_kpa` |
| `flow_cm_s` | float | no | Airflow speed, cm/s |
| `flow_direction` | enum | no | `concurrent`, `opposed`, `quiescent`, `mixed` |
| `gravity` | string | yes | `microgravity`, `1g`, `partial-g` |
| `ignition` | string | no | Ignition method |
| `spread_rate_mm_s` | float | no | Flame spread rate, mm/s |
| `spread_rate_uncertainty` | float | no | Uncertainty, mm/s |
| `burn_length_mm` | float | no | Burn/pyrolysis length, mm |
| `duration_s` | float | no | Test duration, s |
| `outcome` | string | no | `spread`, `no-spread`, `extinguished`, etc. |
| `value_type` | enum | yes | `measured`, `reported`, `estimated` |
| `source_locator` | string | yes | Table/figure/page/DOI |
| `notes` | text | no | Caveats |

### Value type rules

| Value | Meaning |
|---|---|
| `measured` | Extracted from a data table or direct measurement |
| `reported` | Stated in the paper text or abstract |
| `estimated` | Read from a figure or derived; lower confidence |

> If a number cannot be sourced, leave it blank or omit the row. Do not guess.

---

## 4. `sources.json`

```json
{
  "S1": {
    "investigation_id": "saffire-i",
    "type": "paper",
    "title": "...",
    "url": "...",
    "doi": "...",
    "psi_id": "PSI-98",
    "locator": "Table 2",
    "confidence": "high",
    "verified": false
  }
}
```

### Source types

`psi-metadata`, `paper`, `abstract`, `standard`, `challenge-resource`, `image`, `other`.

---

## 5. Units

| Quantity | Unit | Notes |
|---|---|---|
| Oxygen concentration | `%` | Volume percent |
| Total pressure | `kPa` | Convert psi → kPa: `1 psi = 6.89476 kPa` |
| Partial pressure of O₂ | `kPa` | Computed, not hand-entered |
| Flow speed | `cm/s` | Keep as cm/s in data; convert for display if needed |
| Flame spread rate | `mm/s` | Convert cm/s → mm/s: multiply by 10 |
| Length | `mm` | |
| Time | `s` | |
| Gravity | label | `microgravity`, `1g`, `partial-g` |

---

## 6. Validation rules

- `id` is unique and lowercase.
- `investigation_id` exists in `investigations.csv`.
- `o2_pct` is between 0 and 100.
- `pressure_kpa` > 0.
- `ppO2_kpa` equals `o2_pct / 100 * pressure_kpa` within 0.1.
- `flow_cm_s` ≥ 0.
- `spread_rate_mm_s` ≥ 0 or blank.
- `value_type` ∈ {measured, reported, estimated}.
- `confidence` ∈ {high, medium, low}.
- Every numeric value has a `source_locator`.
- No duplicate test IDs.
- No required field is blank.
- Units are consistent; do not mix psi and kPa in the same column.

---

## 7. Core 12

| ID | Investigation | Phase |
|---|---|---|
| `bass` | BASS | Prevention |
| `bass-ii` | BASS-II | Prevention |
| `saffire-i` | Saffire-I | Prevention |
| `saffire-ii` | Saffire-II | Prevention |
| `saffire-iii` | Saffire-III | Prevention |
| `flex` | FLEX | Suppression |
| `flex-2` | FLEX-2 | Suppression |
| `same` | SAME | Detection |
| `same-r` | SAME-R | Detection |
| `acme-bre` | ACME BRE | Prevention |
| `acme-cfi-g` | ACME CFI-G | Prevention |
| `spice` | SPICE | Prevention |

### Optional 7

`acme-cld-flame`, `acme-e-field`, `acme-s-flames`, `cfi`, `daft`, `slice`, `same-utilization`.

---

## 8. Phase mapping

| Phase | Investigations |
|---|---|
| **Prevention** | BASS, BASS-II, Saffire I–III, ACME BRE, ACME CFI-G, SPICE, optional ACME/CFI/SLICE |
| **Detection** | SAME, SAME-R, optional DAFT/DAFT-2 |
| **Suppression** | FLEX, FLEX-2 |

---

## 9. Curation workflow

1. Open the PSI page and NTRS paper.
2. Fill one `investigations.csv` row.
3. Extract 2–4 representative `test_conditions.csv` rows from tables or figures.
4. Add the source to `sources.json` with a locator.
5. Mark `value_type` and `confidence`.
6. Run the validation script.
7. Update `PROGRESS.md` metrics.

> **Reminder:** No curation before the event starts.
