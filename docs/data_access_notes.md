# Data access notes

## ORNL EAGLE-I

The full EAGLE-I archive can be large and may require downloading through an ORNL/DOE/Globus route depending on which portal path you use. This repository is designed so the raw file is not committed to GitHub.

Use one of these approaches:

### Approach A: full 2022 file

1. Download the 2022 EAGLE-I CSV from ORNL/DOE.
2. Rename it to:

```text
eaglei_outages_2022.csv
```

3. Place it in:

```text
data/raw/
```

4. Run the project scripts.

### Approach B: Florida export from portal

If the ORNL Open Energy Data Portal lets you filter to Florida and export a smaller CSV, save that export anywhere and pass it to the slicer:

```bash
python -m src.01_slice_eaglei_ian \
  --input path/to/florida_export.csv \
  --output data/processed/ian_florida_outages_2022.csv
```

The slicer is still useful because it standardizes headers, pads FIPS codes, enforces the Ian time window, and outputs predictable field names.

## Expected outage columns

The script accepts common variants of these fields:

- timestamp/date/time
- FIPS code/GEOID
- county name
- state name or state abbreviation
- customers without power/customers out

If the ORNL export has a header that does not match, open the CSV header and add the new field name to `src/utils.py` in the relevant alias list.

## Census county boundaries

The Census county file is public and small enough to download directly:

```bash
python -m src.00_download_counties
```

If that fails, manually download:

```text
https://www2.census.gov/geo/tiger/GENZ2022/shp/cb_2022_us_county_500k.zip
```

and place it in:

```text
data/raw/cb_2022_us_county_500k.zip
```
