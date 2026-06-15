# QGIS cartography spec — the final map

This is the part the screening is actually about, and it is the part only you can
do: the pipeline hands you a clean GeoPackage, and you build the map in QGIS and
own every decision in it. Work through this yourself rather than treating it as a
checklist someone else produced — in an interview you will be asked *why* you
classified the data the way you did, and these notes explain the why so the
answers are yours.

The layer to map is `data/processed/florida_ian_peak_outages.gpkg`, layer
`florida_counties_peak_outage`, field `peak_customers_out`. The companion field
`has_outage_record` tells you which counties actually had data.

## 1. Coordinate reference system

The Census file arrives in NAD83 geographic coordinates (EPSG:4269), which is
fine for storage but stretches Florida if you map in it directly. Set the
**project CRS** to a projected, area-true system before laying out:

- EPSG:5070 (NAD83 / Conus Albers) — equal-area, the safe default for a
  thematic map where polygon size should read honestly, or
- EPSG:6439 (NAD83(2011) / Florida GDL Albers) — tuned for Florida specifically.

Project → Properties → CRS, set one of these. Being able to say "I mapped in an
equal-area projection so county sizes aren't misleading" is exactly the kind of
detail a reviewer listens for.

## 2. Classification — the decision that matters most

Right-click the layer → Properties → Symbology → **Graduated**, value
`peak_customers_out`.

Choose the classification method deliberately:

- **Natural Breaks (Jenks)** is usually the best fit here. Outage peaks are
  heavily skewed — a few landfall counties dwarf the rest — and Jenks finds the
  natural gaps in that distribution, so the map separates "catastrophic" from
  "severe" from "minor" rather than splitting on arbitrary round numbers.
- **Quantiles** gives each class the same number of counties; useful for an even
  visual spread, but it can place near-identical counties in different classes
  and exaggerate small differences. Mention it as the alternative you considered.
- Avoid **Equal Interval** for this data: with one or two extreme counties, most
  of the map collapses into the lowest class and the gradient is wasted.

Use 5 classes to start. Round the class boundaries to clean numbers
(Symbology → Classes → edit the values) so the legend reads cleanly, e.g.
0–10k, 10k–50k, 50k–100k, 100k–200k, 200k+. Set the boundaries from the real data
you see, not from this example.

## 3. Colour ramp

`peak_customers_out` is a **sequential** quantity (low to high magnitude), so use
a **single-hue sequential ramp** — light = fewer customers out, dark = more.
QGIS ships ColorBrewer ramps; "Reds" or "YlOrRd" read intuitively for an impact
map. Do **not** use a diverging ramp (e.g. blue-to-red): diverging ramps imply a
meaningful midpoint, which this data does not have, and it is a common giveaway
that someone reached for a default without thinking.

## 4. The "no record" counties — an honesty detail

Counties with no record in the slice were filled with `peak_customers_out = 0` by
the join, but **zero customers out and no data are not the same thing**. Don't let
a no-data county render in the lightest "0" colour as if it sailed through the
storm. Either:

- add a rule or a separate category that paints `has_outage_record = false`
  counties in a neutral grey with a "No record" legend entry, or
- filter them out and note the coverage in your write-up.

Calling this out — "I separated no-data from genuine zeros so the map doesn't
overstate coverage" — is a strong point in a walkthrough.

## 5. Labels and the landfall story

Label the top few counties (Properties → Labels → Single labels on
`county_name`, or filter labels to the highest class). Keep it to the handful that
carry the story — the southwest Florida landfall cluster — rather than labelling
all 67. A halo/buffer on the label keeps it legible over dark fills.

## 6. Print layout

Project → New Print Layout. Include, at minimum:

- the map frame at your chosen CRS;
- a **title** ("Hurricane Ian: peak customers without power by Florida county");
- a short **subtitle** with the event window dates;
- a **legend** (rename the field to a plain-English label, not `peak_customers_out`);
- a **scale bar** and a **north arrow**;
- a **data source + CRS note** ("Outage data: ORNL EAGLE-I 2022. Geography:
  US Census 2022 cartographic county boundaries. Projection: NAD83 Conus Albers.");
- your **name and the date**.

Consider adding the restoration-curve PNG (from `restoration_curve`) as an inset
or a second page, so the layout tells the whole story: where it hit hardest, and
how recovery progressed.

## 7. Export

Layout → Export as PDF (vector, sharp at any zoom — the portfolio version) and
Export as Image → PNG at 300 dpi (for the web page and README). Save the QGIS
project as `qgis/hurricane_ian_florida.qgz` and commit it so the map is
reproducible, not just a flat picture.

## What to capture for the portfolio

- the exported PDF and PNG of the final layout;
- a screenshot of the QGIS symbology panel showing your classification;
- a screenshot of the attribute table after the join (proof the spatial join
  populated);
- one or two sentences on why you chose Jenks and a sequential ramp.

That bundle — the map, the choices behind it, and the evidence you produced it —
is what makes this genuinely your QGIS work.
