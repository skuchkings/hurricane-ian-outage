# Session 1: Build the joined Florida outage layer in QGIS

Goal: create a permanent Florida county layer with peak Hurricane Ian outage impact joined to county polygons.

## Inputs

- `data/raw/cb_2022_us_county_500k.zip`
- `data/processed/ian_florida_outages_2022.csv`
- or the script-derived peak table: `data/processed/ian_peak_outages_by_county.csv`

## Recommended path: use the scripted join

If you already ran the scripts, load this file directly:

```text
data/processed/florida_ian_peak_outages.gpkg
```

Layer name:

```text
florida_counties_peak_outage
```

Open the attribute table and confirm these fields exist:

- `GEOID`
- `NAME`
- `peak_timestamp`
- `peak_customers_out`
- `peak_rank_statewide`

That is your joined analytical layer.

## Manual QGIS path

Use this when you want to demonstrate the join process in screenshots.

### 1. Load counties

1. Drag `cb_2022_us_county_500k.shp` into QGIS.
2. Right-click the layer → **Filter**.
3. Set the filter:

```sql
"STATEFP" = '12'
```

4. Check the CRS shown at the bottom right. The Census file should load as NAD83 / EPSG:4269.

### 2. Load outage slice as an attribute table

1. Layer → Add Layer → Add Delimited Text Layer.
2. Select `data/processed/ian_florida_outages_2022.csv`.
3. Set geometry to **No geometry (attribute-only table)**.
4. Confirm fields: `timestamp`, `fips_code`, `county_name`, `state_name`, `customers_out`.

### 3. Aggregate to peak per county

1. Processing Toolbox → search **Statistics by categories**.
2. Input layer: outage table.
3. Field to calculate statistics on: `customers_out`.
4. Field with categories: `fips_code`.
5. Run.

The output table contains a maximum value per county. Rename or remember the maximum field; it may appear as `max`, `customers_out_max`, or similar depending on QGIS version.

### 4. Join to polygons

1. Right-click the Florida county polygon layer → Properties → Joins.
2. Add a join.
3. Join layer: statistics output.
4. Join field: `fips_code` or category field.
5. Target field: `GEOID`.
6. Apply.

Both fields should be five-character strings such as `12071`, so the join should match cleanly.

### 5. Save as permanent GeoPackage

1. Right-click the joined Florida county layer.
2. Export → Save Features As.
3. Format: GeoPackage.
4. File: `data/processed/florida_ian_peak_outages.gpkg`.
5. Layer name: `florida_counties_peak_outage`.
6. CRS: keep source CRS or reproject to EPSG:5070 for mapping.

## Quality checks

- Florida should have 67 county polygons.
- `GEOID` values should start with `12`.
- Hard-hit southwest counties should have non-zero peak outage values.
- Counties outside the Ian impact area may have lower values or no record depending on the outage slice.
