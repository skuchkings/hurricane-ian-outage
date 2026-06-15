#!/usr/bin/env python3
"""Calculate peak customers without power by Florida county."""

from __future__ import annotations

import argparse

import pandas as pd

from ianoutage.utils import ensure_parent_dir, standardize_fips


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/ian_florida_outages_2022.csv")
    parser.add_argument("--output", default="data/processed/ian_peak_outages_by_county.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input, parse_dates=["timestamp"], dtype={"fips_code": "string"})
    df["fips_code"] = standardize_fips(df["fips_code"])
    df["customers_out"] = pd.to_numeric(df["customers_out"], errors="coerce").fillna(0).astype("int64")

    idx = df.groupby("fips_code")["customers_out"].idxmax()
    peaks = (
        df.loc[idx, ["fips_code", "county_name", "state_name", "timestamp", "customers_out"]]
        .rename(columns={"timestamp": "peak_timestamp", "customers_out": "peak_customers_out"})
        .sort_values("peak_customers_out", ascending=False)
    )

    # Useful portfolio rank field for labels and top-five callouts.
    peaks["peak_rank_statewide"] = range(1, len(peaks) + 1)

    output = ensure_parent_dir(args.output)
    peaks.to_csv(output, index=False)
    print(f"Counties: {len(peaks):,}")
    print(f"Saved: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
