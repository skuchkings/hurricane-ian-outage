#!/usr/bin/env python3
"""Create an optional static choropleth map in Python.

The QGIS layout remains the recommended final portfolio output. This script is
useful for a quick GitHub preview or automated sanity check.
"""

from __future__ import annotations

import argparse

import geopandas as gpd
import matplotlib.pyplot as plt

from ianoutage.utils import ensure_parent_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/florida_ian_peak_outages.gpkg")
    parser.add_argument("--layer", default="florida_counties_peak_outage")
    parser.add_argument("--output", default="data/outputs/ian_florida_peak_outage_map.png")
    parser.add_argument("--title", default="Hurricane Ian: Peak customers without power by Florida county")
    args = parser.parse_args()

    gdf = gpd.read_file(args.input, layer=args.layer)
    if gdf.crs is None:
        raise ValueError("Input geography has no CRS.")

    # Albers Equal Area is a better cartographic CRS for a Florida thematic map
    # than raw latitude/longitude.
    gdf = gdf.to_crs("EPSG:5070")

    fig, ax = plt.subplots(figsize=(8, 10))
    gdf.plot(
        column="peak_customers_out",
        ax=ax,
        legend=True,
        scheme="Quantiles",
        k=5,
        missing_kwds={"label": "No record"},
        edgecolor="0.7",
        linewidth=0.25,
    )
    ax.set_axis_off()
    ax.set_title(args.title, fontsize=14)
    ax.annotate(
        "Data: ORNL EAGLE-I 2022 outage records; geography: U.S. Census 2022 county cartographic boundaries",
        xy=(0.5, 0.02),
        xycoords="figure fraction",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout()

    output = ensure_parent_dir(args.output)
    fig.savefig(output, dpi=250)
    plt.close(fig)
    print(f"Saved: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
