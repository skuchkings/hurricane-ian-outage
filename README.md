# Hurricane Ian — Florida Power Outage GIS Analysis

A reproducible, county-level geospatial analysis of Hurricane Ian's impact on the
Florida electricity grid (landfall 28 September 2022), built from public data:
peak outage impact by county, duration-weighted severity, a statewide restoration
curve, and a print-ready QGIS choropleth.

**Core questions.** Which Florida counties experienced the highest peak number of
customers without power? Which suffered the most *total* disruption once duration
is accounted for? And how quickly did the state recover after the peak?

## Project status — read this first

This repository is the **analysis machinery and the plan**. Two things turn it
into a finished portfolio piece, and both are yours to do:

1. **Run the pipeline on the real EAGLE-I 2022 file.** No real outage data ships
   here — only a tiny synthetic sample (`data/sample/`) for testing the code. Until
   you run the real data, there are no results, and `build_report` will refuse to
   produce any (by design — figures come from a real run, never by hand).
2. **Build the final map in QGIS yourself**, following `qgis/cartography_spec.md`.
   The QGIS layout is the deliverable the screening is actually asking about, and
   it is the part that makes this genuinely your work — you should be able to walk
   an interviewer through every classification and colour choice in it.

What is already done: a validated, tested pipeline; a corrected, importable
package; analytical depth (customer-hours severity, per-county restoration);
self-validation; reproducible reporting; and a full cartography guide.

## Public data sources

**Outage data — ORNL EAGLE-I Power Outage Data 2014–2022.** County-level records
at 15-minute intervals (FIPS, county, state, customers without power, timestamp).
DOI `10.13139/ORNLNCCS/1975202`. See `docs/data_access_notes.md` for the download
routes (the full archive is delivered via Globus and needs a free account; the
ORNL Open Energy Data Portal also offers browsable exports). Save the 2022 file as
`data/raw/eaglei_outages_2022.csv`.

**Geography — US Census 2022 Cartographic Boundary File, county, 1:500,000.**
`cb_2022_us_county_500k.zip`. Fetch with `python -m ianoutage.download_counties`
or download manually from www2.census.gov.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# or:  conda env create -f environment.yml && conda activate hurricane-ian-outage
```

## Run

```bash
make sample      # validate the pandas chain on the synthetic sample (no geopandas)
make test        # unit tests

# the real thing, once data/raw/eaglei_outages_2022.csv is in place:
python -m ianoutage.download_counties
bash run_all.sh
```

`run_all.sh` runs, in order: slice → peak-by-county → severity → restoration curve
→ validate → spatial join → Python map preview → results report. Then you open
`data/processed/florida_ian_peak_outages.gpkg` in QGIS and build the layout.

## Pipeline modules (`ianoutage/`)

| Module | What it does |
| --- | --- |
| `slice_eaglei` | Chunk-reads the national CSV, standardizes headers, keeps Florida + the Ian window, preserves 5-digit FIPS. |
| `peak_by_county` | Peak customers-out per county, with the timestamp and a statewide rank. |
| `severity` | Customer-hours of outage (trapezoidal integral) and per-county restoration time to 10% of peak. |
| `restoration_curve` | Statewide outage time series, peak, and restoration milestones; plots the curve. |
| `join_counties` | Joins peaks to Census county polygons on GEOID; keeps all 67 counties and flags which had records; writes GeoPackage + GeoJSON. |
| `validate` | Read-only QA: FIPS, negatives, duplicates, window coverage, rank integrity. Non-zero exit on hard failures. |
| `make_map` | Optional Python choropleth preview in equal-area projection. |
| `build_report` | Writes `docs/RESULTS.md` straight from the pipeline outputs; refuses to run without them. |
| `download_counties` | Fetches and validates the Census county zip. |

## What changed from the first version

- Fixed the package so it actually imports and runs (the original `from src.*`
  imports and `python -m src.01_*` commands could not execute as shipped).
- Added **customer-hours severity** and **per-county restoration time** — peak
  alone misses how long a county stayed dark.
- Added a **validation** step so the analysis checks its own outputs.
- Added **reproducible reporting** (`build_report`) so write-up figures come only
  from a real run.
- Added a detailed **QGIS cartography spec** (CRS, Jenks vs quantiles, sequential
  ramp, the no-data-vs-zero distinction, layout, export).
- Added tests for the new logic; made `tqdm` optional and the integration
  NumPy-2-safe.

## What this demonstrates (once executed)

Working with large public infrastructure data; chunked processing; FIPS/GEOID
hygiene; spatial joins; duration-aware severity analysis; self-validating
pipelines; reproducible reporting; and deliberate thematic cartography in QGIS.

## Caveat

EAGLE-I counts utility customers without power, not individual people; a customer
may be a meter, household, or account. Treat figures as a strong county-level
indicator, not an exact person-level count.
