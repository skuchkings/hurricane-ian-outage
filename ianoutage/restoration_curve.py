#!/usr/bin/env python3
"""Build the Florida outage restoration curve after Hurricane Ian."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from ianoutage.utils import ensure_parent_dir, standardize_fips


def first_time_at_or_below(df_after_peak: pd.DataFrame, threshold: float) -> str | None:
    hit = df_after_peak[df_after_peak["pct_of_peak"] <= threshold]
    if hit.empty:
        return None
    return hit.iloc[0]["timestamp"].isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/ian_florida_outages_2022.csv")
    parser.add_argument("--curve-csv", default="data/processed/ian_florida_restoration_curve.csv")
    parser.add_argument("--metrics-json", default="data/processed/ian_florida_restoration_metrics.json")
    parser.add_argument("--plot", default="data/outputs/ian_florida_restoration_curve.png")
    args = parser.parse_args()

    df = pd.read_csv(args.input, parse_dates=["timestamp"], dtype={"fips_code": "string"})
    df["fips_code"] = standardize_fips(df["fips_code"])
    df["customers_out"] = pd.to_numeric(df["customers_out"], errors="coerce").fillna(0)

    curve = (
        df.groupby("timestamp", as_index=False)["customers_out"]
        .sum()
        .rename(columns={"customers_out": "florida_customers_out"})
        .sort_values("timestamp")
    )
    if curve.empty:
        raise ValueError("No records found in input slice.")

    peak_idx = curve["florida_customers_out"].idxmax()
    peak_value = float(curve.loc[peak_idx, "florida_customers_out"])
    peak_timestamp = curve.loc[peak_idx, "timestamp"]

    curve["pct_of_peak"] = curve["florida_customers_out"] / peak_value if peak_value else 0
    curve["pct_restored_from_peak"] = 1 - curve["pct_of_peak"]
    after_peak = curve[curve["timestamp"] >= peak_timestamp].copy()

    metrics = {
        "state_peak_customers_out": int(peak_value),
        "state_peak_timestamp": peak_timestamp.isoformat(),
        "first_time_below_50pct_of_peak": first_time_at_or_below(after_peak, 0.50),
        "first_time_below_25pct_of_peak": first_time_at_or_below(after_peak, 0.25),
        "first_time_below_10pct_of_peak": first_time_at_or_below(after_peak, 0.10),
        "first_time_below_5pct_of_peak": first_time_at_or_below(after_peak, 0.05),
    }

    curve_csv = ensure_parent_dir(args.curve_csv)
    metrics_json = ensure_parent_dir(args.metrics_json)
    plot_path = ensure_parent_dir(args.plot)

    curve.to_csv(curve_csv, index=False)
    metrics_json.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(curve["timestamp"], curve["florida_customers_out"])
    ax.axvline(peak_timestamp, linestyle="--", linewidth=1)
    ax.set_title("Florida customers without power during Hurricane Ian")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Customers without power")
    ax.ticklabel_format(axis="y", style="plain")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(plot_path, dpi=200)
    plt.close(fig)

    print(f"Peak: {int(peak_value):,} at {peak_timestamp}")
    print(f"Saved: {curve_csv}")
    print(f"Saved: {metrics_json}")
    print(f"Saved: {plot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
