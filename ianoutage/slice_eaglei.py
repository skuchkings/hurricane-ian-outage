#!/usr/bin/env python3
"""Slice the national EAGLE-I 2022 outage CSV to Florida during Hurricane Ian.

The EAGLE-I public files are large. This script reads the input in chunks,
standardizes common header variants, filters to Florida and the requested time
window, and writes a compact CSV for QGIS and downstream analysis.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from tqdm import tqdm
except ImportError:  # tqdm is a convenience, not a requirement
    def tqdm(iterable, **kwargs):
        return iterable

from ianoutage.config import DEFAULT_END, DEFAULT_START, FLORIDA_STATE_ABBR, FLORIDA_STATE_NAME, FLORIDA_STATEFP
from ianoutage.utils import (
    COUNTY_ALIASES,
    CUSTOMERS_OUT_ALIASES,
    FIPS_ALIASES,
    STATE_ALIASES,
    TIMESTAMP_ALIASES,
    ensure_parent_dir,
    first_existing,
    normalize_columns,
    safe_to_numeric,
    standardize_fips,
)

STANDARD_COLUMNS = ["timestamp", "fips_code", "county_name", "state_name", "customers_out"]


def standardize_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    chunk = normalize_columns(chunk)
    ts_col = first_existing(chunk.columns, TIMESTAMP_ALIASES, "timestamp")
    fips_col = first_existing(chunk.columns, FIPS_ALIASES, "FIPS")
    customers_col = first_existing(chunk.columns, CUSTOMERS_OUT_ALIASES, "customers without power")

    county_col = next((c for c in COUNTY_ALIASES if c in chunk.columns), None)
    state_col = next((c for c in STATE_ALIASES if c in chunk.columns), None)

    out = pd.DataFrame()
    out["timestamp"] = pd.to_datetime(chunk[ts_col], errors="coerce")
    out["fips_code"] = standardize_fips(chunk[fips_col])
    out["county_name"] = chunk[county_col].astype("string").str.strip() if county_col else pd.NA
    out["state_name"] = chunk[state_col].astype("string").str.strip() if state_col else pd.NA
    out["customers_out"] = safe_to_numeric(chunk[customers_col]).astype("int64")
    return out


def filter_florida_ian(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    state_match = df["state_name"].str.lower().isin(
        [FLORIDA_STATE_NAME.lower(), FLORIDA_STATE_ABBR.lower()]
    )
    fips_match = df["fips_code"].str.startswith(FLORIDA_STATEFP, na=False)
    time_match = df["timestamp"].between(start, end, inclusive="both")
    return df[(state_match | fips_match) & time_match].copy()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Raw EAGLE-I 2022 CSV")
    parser.add_argument("--output", default="data/processed/ian_florida_outages_2022.csv")
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--chunksize", type=int, default=500_000)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = ensure_parent_dir(args.output)
    start = pd.Timestamp(args.start)
    end = pd.Timestamp(args.end)

    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    if output_path.exists():
        output_path.unlink()

    rows_written = 0
    reader = pd.read_csv(input_path, chunksize=args.chunksize, low_memory=False)
    for chunk in tqdm(reader, desc="Filtering EAGLE-I chunks"):
        slim = standardize_chunk(chunk)
        filtered = filter_florida_ian(slim, start, end)
        if filtered.empty:
            continue
        filtered = filtered[STANDARD_COLUMNS].sort_values(["timestamp", "fips_code"])
        filtered.to_csv(output_path, mode="a", index=False, header=(rows_written == 0))
        rows_written += len(filtered)

    print(f"Rows written: {rows_written:,}")
    print(f"Saved: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
