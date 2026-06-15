#!/usr/bin/env bash
# Run the full pipeline from the repo root. Requires the real EAGLE-I 2022 CSV
# in data/raw/ and the Census county zip (00_download or manual). geopandas is
# required for the join and map steps (see environment.yml / requirements.txt).
set -euo pipefail
export PYTHONPATH="${PYTHONPATH:-.}"

RAW_EAGLEI="${1:-data/raw/eaglei_outages_2022.csv}"
COUNTIES_ZIP="${2:-data/raw/cb_2022_us_county_500k.zip}"

python -m ianoutage.slice_eaglei --input "$RAW_EAGLEI"
python -m ianoutage.peak_by_county
python -m ianoutage.severity
python -m ianoutage.restoration_curve
python -m ianoutage.validate
python -m ianoutage.join_counties --counties "$COUNTIES_ZIP"
python -m ianoutage.make_map
python -m ianoutage.build_report

echo
echo "Pipeline complete. Next: open the GeoPackage in QGIS and build the map"
echo "following qgis/cartography_spec.md. The QGIS layout is the final deliverable."
