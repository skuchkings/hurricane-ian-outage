# Session 2: Style, layout, export, and restoration curve

Goal: produce a portfolio-quality choropleth map and a restoration curve graphic.

## 1. Load the joined layer

Open QGIS and load:

```text
data/processed/florida_ian_peak_outages.gpkg
```

Layer:

```text
florida_counties_peak_outage
```

## 2. Reproject for layout

For a cleaner map, export or set the project/layer display to an equal-area projection, such as:

```text
EPSG:5070 — NAD83 / Conus Albers
```

EPSG:4269 is fine for data storage, but EPSG:5070 is better for a thematic map.

## 3. Choropleth styling

1. Right-click layer → Properties → Symbology.
2. Choose **Graduated**.
3. Value field:

```text
peak_customers_out
```

4. Classification: Natural Breaks (Jenks) or Quantile.
5. Classes: 5.
6. Mode note:
   - Use **Natural Breaks** if the top southwest counties are extreme and you want the story to pop.
   - Use **Quantile** if you want a more evenly distributed legend.
7. Set null or zero outage counties to a very light neutral fill.
8. Add thin gray county outlines.

Suggested legend title:

```text
Peak customers without power
```

## 4. Labels and callouts

Label only the highest-impact counties to avoid clutter:

1. Layer Properties → Labels.
2. Single labels using `NAME`.
3. Use rule-based labeling:

```sql
"peak_rank_statewide" <= 5
```

Optional callout label expression:

```qgis
concat("NAME", '\n', format_number("peak_customers_out", 0))
```

## 5. Print layout

Create a new layout.

Recommended page:

```text
Letter portrait or A4 portrait
```

Add these elements:

- Title: **Hurricane Ian Peak Power Outage Impact Across Florida**
- Subtitle: **Maximum county-level customers without power during 26 Sep–10 Oct 2022**
- Main map
- Legend
- Scale bar
- North arrow
- Source note
- Small methodology note

Source note:

```text
Outage data: ORNL EAGLE-I 2022 county outage records. Geography: U.S. Census Bureau 2022 county cartographic boundary file, 1:500,000 scale. Metric: maximum reported customers without power per county within the Hurricane Ian analysis window.
```

Method note:

```text
FIPS-coded 15-minute outage records were filtered to Florida, aggregated to each county's peak customers-out value, and joined to Census county polygons by GEOID.
```

## 6. Export final map

Export two versions:

```text
data/outputs/hurricane_ian_florida_peak_outage_map.pdf
data/outputs/hurricane_ian_florida_peak_outage_map.png
```

For PNG, use at least 300 dpi.

## 7. Restoration curve

If you ran `src.04_restoration_curve`, use:

```text
data/outputs/ian_florida_restoration_curve.png
```

Or import this CSV into QGIS/Excel/Notebook:

```text
data/processed/ian_florida_restoration_curve.csv
```

Key fields:

- `timestamp`
- `florida_customers_out`
- `pct_of_peak`
- `pct_restored_from_peak`

Suggested chart title:

```text
Florida outage restoration curve after Hurricane Ian
```

Suggested interpretation:

```text
The curve rises into the statewide outage peak, then falls as power is restored. The first timestamp below 50%, 25%, 10%, and 5% of peak outage level gives a simple, defensible restoration timeline.
```
