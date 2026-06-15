# Data dictionary

## `ian_florida_outages_2022.csv`

Derived from the raw ORNL EAGLE-I 2022 outage file after filtering to Florida and the Hurricane Ian analysis window.

| Field | Type | Description |
|---|---:|---|
| `timestamp` | datetime | EAGLE-I outage record timestamp. |
| `fips_code` | string | Five-digit county FIPS code, padded with leading zeros when needed. |
| `county_name` | string | County name from EAGLE-I record. |
| `state_name` | string | State name or abbreviation from EAGLE-I record. |
| `customers_out` | integer | Reported customers without power. A customer is not necessarily an individual person. |

## `ian_peak_outages_by_county.csv`

County-level peak impact table.

| Field | Type | Description |
|---|---:|---|
| `fips_code` | string | Five-digit county FIPS code. |
| `county_name` | string | County name. |
| `state_name` | string | State name. |
| `peak_timestamp` | datetime | Timestamp when the county reached its maximum customers-out value during the analysis window. |
| `peak_customers_out` | integer | Maximum reported customers without power in that county during the analysis window. |
| `peak_rank_statewide` | integer | Rank of the county by peak outage impact, descending. |

## `florida_ian_peak_outages.gpkg`

Florida county geometry with outage metrics joined.

Important fields from Census:

| Field | Type | Description |
|---|---:|---|
| `STATEFP` | string | State FIPS code. Florida = `12`. |
| `COUNTYFP` | string | County FIPS code within state. |
| `GEOID` | string | Full five-digit county FIPS/GEOID. |
| `NAME` | string | County name. |
| `geometry` | geometry | County polygon or multipolygon. |

Important joined fields:

| Field | Type | Description |
|---|---:|---|
| `peak_customers_out` | integer | Peak outage impact. |
| `peak_timestamp` | datetime | Time of county peak outage. |
| `peak_rank_statewide` | integer | Statewide county rank by peak outage impact. |
| `has_outage_record` | boolean | Whether the county matched a record in the outage slice. |

## `ian_florida_restoration_curve.csv`

Statewide outage time series aggregated across Florida counties.

| Field | Type | Description |
|---|---:|---|
| `timestamp` | datetime | EAGLE-I timestamp. |
| `florida_customers_out` | number | Sum of reported customers without power across Florida counties at that timestamp. |
| `pct_of_peak` | number | Outage level divided by statewide peak outage level. |
| `pct_restored_from_peak` | number | `1 - pct_of_peak`; a simple restoration-from-peak measure. |
