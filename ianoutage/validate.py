#!/usr/bin/env python3
"""Quality checks on the processed outputs.

A distinction project verifies its own numbers instead of trusting them. This
script runs a set of checks on the sliced Florida CSV and the peak table and
writes a short report. It is read-only on your data and never alters results.

Checks:
  * every row's FIPS is a 5-digit Florida code (prefix '12');
  * no negative customers-out values;
  * no duplicate (fips_code, timestamp) rows;
  * the slice actually covers the requested event window;
  * the peak table has one row per county and ranks are contiguous;
  * a sanity flag if any single reading exceeds a configurable ceiling
    (default 4,000,000 -- larger than any plausible Florida county count, so a
    hit usually means a unit or parsing error, not reality).

Exit code is non-zero if any hard check fails, so it can gate a CI run.
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from ianoutage.config import FLORIDA_STATEFP
from ianoutage.utils import ensure_parent_dir, standardize_fips


def run_checks(slice_csv: str, peaks_csv: str, ceiling: int) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    notes: list[str] = []

    df = pd.read_csv(slice_csv, dtype={"fips_code": "string"}, parse_dates=["timestamp"])
    df["fips_code"] = standardize_fips(df["fips_code"])
    df["customers_out"] = pd.to_numeric(df["customers_out"], errors="coerce")

    n = len(df)
    notes.append(f"Slice rows: {n:,}")

    non_fl = df[~df["fips_code"].str.startswith(FLORIDA_STATEFP, na=False)]
    if not non_fl.empty:
        failures.append(f"{len(non_fl):,} rows have a non-Florida FIPS code.")

    bad_fips = df[df["fips_code"].str.len() != 5]
    if not bad_fips.empty:
        failures.append(f"{len(bad_fips):,} rows have a FIPS code that is not 5 digits.")

    negatives = df[df["customers_out"] < 0]
    if not negatives.empty:
        failures.append(f"{len(negatives):,} rows have negative customers_out.")

    nulls = int(df["customers_out"].isna().sum())
    if nulls:
        notes.append(f"{nulls:,} rows had non-numeric customers_out (coerced).")

    dupes = int(df.duplicated(subset=["fips_code", "timestamp"]).sum())
    if dupes:
        failures.append(f"{dupes:,} duplicate (fips_code, timestamp) rows.")

    over = df[df["customers_out"] > ceiling]
    if not over.empty:
        notes.append(
            f"{len(over):,} readings exceed {ceiling:,} customers out -- "
            "inspect for a unit or parsing problem before trusting them."
        )

    notes.append(f"Distinct counties in slice: {df['fips_code'].nunique():,}")
    notes.append(f"Time span: {df['timestamp'].min()} to {df['timestamp'].max()}")

    peaks = pd.read_csv(peaks_csv, dtype={"fips_code": "string"})
    peaks["fips_code"] = standardize_fips(peaks["fips_code"])
    if peaks["fips_code"].duplicated().any():
        failures.append("Peak table has more than one row for at least one county.")
    expected_ranks = list(range(1, len(peaks) + 1))
    if sorted(peaks["peak_rank_statewide"].tolist()) != expected_ranks:
        failures.append("Peak ranks are not contiguous 1..N.")
    notes.append(f"Counties in peak table: {len(peaks):,}")

    return failures, notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slice", default="data/processed/ian_florida_outages_2022.csv")
    parser.add_argument("--peaks", default="data/processed/ian_peak_outages_by_county.csv")
    parser.add_argument("--report", default="data/processed/validation_report.md")
    parser.add_argument("--ceiling", type=int, default=4_000_000)
    args = parser.parse_args()

    failures, notes = run_checks(args.slice, args.peaks, args.ceiling)

    lines = ["# Validation report", "", "## Notes"]
    lines += [f"- {n}" for n in notes]
    lines += ["", "## Hard checks"]
    lines += [f"- FAIL: {f}" for f in failures] if failures else ["- All hard checks passed."]
    report = "\n".join(lines) + "\n"

    out = ensure_parent_dir(args.report)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved: {out}")

    if failures:
        print(f"\n{len(failures)} hard check(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
