#!/usr/bin/env python3
"""Join peak outage metrics to 2022 Census Florida county polygons."""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd

from ianoutage.config import CENSUS_COUNTY_2022_500K_URL, FLORIDA_STATEFP
from ianoutage.utils import ensure_parent_dir, standardize_fips


def read_counties(path_or_url: str) -> gpd.GeoDataFrame:
    # Geopandas/pyogrio can read a local zip path directly. For URLs, it can also
    # read direct downloadable zip URLs in many environments.
    gdf = gpd.read_file(path_or_url)
    required = {"STATEFP", "GEOID", "NAME"}
    missing = required - set(gdf.columns)
    if missing:
        raise ValueError(f"County file missing expected Census fields: {missing}")
    return gdf


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--counties", default="data/raw/cb_2022_us_county_500k.zip")
    parser.add_argument("--peaks", default="data/processed/ian_peak_outages_by_county.csv")
    parser.add_argument("--gpkg", default="data/processed/florida_ian_peak_outages.gpkg")
    parser.add_argument("--geojson", default="data/processed/florida_ian_peak_outages.geojson")
    parser.add_argument("--layer", default="florida_counties_peak_outage")
    parser.add_argument(
        "--use-url",
        action="store_true",
        help="Read the Census county ZIP from the public Census URL instead of --counties.",
    )
    args = parser.parse_args()

    counties_src = CENSUS_COUNTY_2022_500K_URL if args.use_url else args.counties
    if not args.use_url and not Path(counties_src).exists():
        raise FileNotFoundError(
            f"County boundary file not found: {counties_src}. "
            "Run src/00_download_counties.py first or pass --use-url."
        )

    counties = read_counties(counties_src)
    florida = counties[counties["STATEFP"].astype(str) == FLORIDA_STATEFP].copy()
    florida["GEOID"] = standardize_fips(florida["GEOID"])

    peaks = pd.read_csv(args.peaks, dtype={"fips_code": "string"}, parse_dates=["peak_timestamp"])
    peaks["fips_code"] = standardize_fips(peaks["fips_code"])

    joined = florida.merge(peaks, how="left", left_on="GEOID", right_on="fips_code")
    joined["peak_customers_out"] = joined["peak_customers_out"].fillna(0).astype("int64")
    joined["has_outage_record"] = joined["fips_code"].notna()

    gpkg = ensure_parent_dir(args.gpkg)
    geojson = ensure_parent_dir(args.geojson)
    joined = joined.loc[:, ~joined.columns.str.lower().duplicated()].copy()
    joined.to_file(gpkg, layer=args.layer, driver="GPKG")
    joined.to_file(geojson, driver="GeoJSON")

    matched = int(joined["has_outage_record"].sum())
    print(f"Florida counties: {len(joined):,}")
    print(f"Counties with outage records in slice: {matched:,}")
    print(f"Saved: {gpkg}")
    print(f"Saved: {geojson}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
