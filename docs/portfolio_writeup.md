# Hurricane Ian Florida Power Outage Impact

## Project summary

This project maps the county-level peak power outage impact of Hurricane Ian across Florida and follows the map with a statewide restoration curve. The goal is to show a complete geospatial RCA-style workflow: public infrastructure data, event-window filtering, county aggregation, spatial join, choropleth mapping, and time-series restoration analysis.

## Why Hurricane Ian

Hurricane Ian made landfall in southwest Florida on 28 September 2022 and caused widespread disruption across the state. The event is well suited for a portfolio piece because the spatial pattern is readable: the highest outage impacts should cluster around the southwest Florida landfall region, while the restoration curve shows recovery over time.

## Data

The outage data comes from ORNL's EAGLE-I Power Outage Data 2014–2022, a county-level dataset with records at 15-minute intervals. The project uses the 2022 outage file and filters it to Florida during the Hurricane Ian analysis window.

The geography comes from the U.S. Census Bureau 2022 cartographic county boundary file at 1:500,000 scale. This simplified boundary file is appropriate for thematic mapping.

## Method

1. Download the 2022 ORNL EAGLE-I outage data and the 2022 Census county boundary shapefile.
2. Read the national outage file in chunks because the raw file is large.
3. Standardize column names and preserve county FIPS codes as five-character strings.
4. Filter records to Florida and the Hurricane Ian event window: 26 September 2022 through 10 October 2022.
5. Group the outage records by county FIPS and calculate the maximum reported customers without power per county.
6. Join the peak outage table to Florida county polygons using Census `GEOID`.
7. Style the joined layer as a graduated choropleth map in QGIS.
8. Aggregate all Florida county records by timestamp to create the statewide restoration curve.
9. Calculate simple restoration milestones: first time below 50%, 25%, 10%, and 5% of statewide peak outage level.

## Key metrics to report after running the data

Do not type these in by hand. Run `python -m ianoutage.build_report` and it
writes `docs/RESULTS.md` with every figure computed directly from your pipeline
outputs:

- statewide peak customers without power, and its timestamp;
- statewide restoration milestones (first below 50%, 25%, 10%, 5% of peak);
- top counties by peak customers out;
- top counties by customer-hours of outage, with per-county restoration time.

Paste the generated figures into the narrative above once they exist. They will
only exist after a real run on the real EAGLE-I file.

## Portfolio value

This project demonstrates practical GIS and data analysis skills that hiring teams can inspect directly:

- reproducible processing scripts;
- transparent data lineage;
- correct use of FIPS/GEOID joins;
- chunked handling of large CSV data;
- county-level aggregation;
- final thematic map design;
- event recovery analysis using a restoration curve.

## Caveats

EAGLE-I reports customers without power, not individual people affected. A customer can represent a meter, household, building, or account depending on the utility reporting context. EAGLE-I coverage is broad but not perfectly complete, so the map should be interpreted as a strong county-level outage indicator rather than an exact person-level impact estimate.
