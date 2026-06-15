# Hurricane Ian Florida Outage -- Results

_Generated 2026-06-14 19:55 UTC from the pipeline outputs listed below. Every figure here was computed by the scripts, not entered by hand._

- Source peak table: `data/processed/ian_peak_outages_by_county.csv`
- Source severity table: `data/processed/ian_county_severity.csv`
- Source restoration metrics: `data/processed/ian_florida_restoration_metrics.json`

## Statewide

- Peak customers without power: **2,500,687**
- Time of statewide peak: **2022-09-29T22:00:00**
- First below 50% of peak: 2022-10-01T10:30:00
- First below 25% of peak: 2022-10-01T13:45:00
- First below 10% of peak: 2022-10-04T07:45:00
- First below 5% of peak: 2022-10-04T07:45:00

## Top 5 counties by peak customers out

| Rank | County | Peak customers out | Peak time |
| ---: | --- | ---: | --- |
| 1 | Lee | 456,573 | 2022-09-29 00:00:00 |
| 2 | Sarasota | 257,410 | 2022-09-29 03:00:00 |
| 3 | Orange | 229,025 | 2022-09-29 16:45:00 |
| 4 | Volusia | 224,435 | 2022-09-29 19:00:00 |
| 5 | Hillsborough | 217,144 | 2022-09-29 11:00:00 |

## Top 5 counties by customer-hours of outage (duration-weighted)

| Rank | County | Customer-hours out | Restoration hrs to 10% |
| ---: | --- | ---: | ---: |
| 1 | Lee | 47,332,701 | 127.75 |
| 2 | Sarasota | 21,439,745 | 6.25 |
| 3 | Charlotte | 16,735,305 | 13.25 |
| 4 | Collier | 15,956,375 | 58.75 |
| 5 | Volusia | 12,401,038 | 95.5 |

## Caveat

EAGLE-I reports utility customers without power, not individual people. A customer may be a meter, household, or account. Figures are a strong county-level indicator, not an exact person-level count.

