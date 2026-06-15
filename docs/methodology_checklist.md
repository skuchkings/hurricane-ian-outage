# Methodology checklist for reviewers

Use this list to explain the project in an interview or portfolio walkthrough.

- I selected Hurricane Ian because it created a clear spatial outage pattern across Florida.
- I used ORNL EAGLE-I because it provides county-level power outage records at 15-minute intervals.
- I used Census cartographic county boundaries because they are simplified for thematic maps.
- I treated FIPS/GEOID as strings, not numbers, so leading zeros are preserved.
- I filtered to Florida using either state name/abbreviation or FIPS prefix `12`.
- I filtered to the event window before aggregation to avoid unrelated outage periods.
- I derived each county's peak outage impact using the maximum customers-out value in the window.
- I joined the derived peak table to county polygons by `fips_code` → `GEOID`.
- I saved the joined layer to GeoPackage so the analysis is reproducible and portable.
- I built the restoration curve by summing Florida county outage records at each timestamp.
- I calculated restoration milestones relative to the statewide peak, not relative to total customers.
- I stated the caveat that customers without power are utility customers/accounts, not individual people.
