#!/usr/bin/env python3
"""Per-county outage severity beyond the instantaneous peak.

Peak customers-out captures the worst single moment, but two counties with the
same peak can differ enormously in how long they stayed dark. This module adds
two duration-aware severity metrics per county:

  * customer_hours_out  -- the area under each county's customers-out curve over
    the event window (trapezoidal integration on the real timestamps, in hours).
    This is the closest single number to "total disruption" the data supports.
  * restoration_hours_to_10pct -- hours from a county's own peak until its
    customers-out first falls to 10% or less of that county's peak. A blank value
    means the county had not recovered to 10% by the end of the slice.

Run AFTER slice_eaglei. It reads the sliced Florida CSV only; it does not invent
or assume any figure. Every number is integrated directly from the input rows.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from ianoutage.utils import ensure_parent_dir, standardize_fips

# np.trapz was renamed to np.trapezoid in NumPy 2.0.
_trapezoid = getattr(np, "trapezoid", getattr(np, "trapz", None))


def county_severity(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fips_code"] = standardize_fips(df["fips_code"])
    df["customers_out"] = pd.to_numeric(df["customers_out"], errors="coerce").fillna(0.0)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values(["fips_code", "timestamp"])

    rows = []
    for fips, g in df.groupby("fips_code"):
        g = g.sort_values("timestamp")
        county = g["county_name"].dropna().iloc[0] if g["county_name"].notna().any() else pd.NA
        state = g["state_name"].dropna().iloc[0] if g["state_name"].notna().any() else pd.NA

        # Hours elapsed from the first reading, used as the integration axis.
        hours = (g["timestamp"] - g["timestamp"].iloc[0]).dt.total_seconds().to_numpy() / 3600.0
        out = g["customers_out"].to_numpy(dtype=float)
        customer_hours = float(_trapezoid(out, hours)) if len(g) > 1 else 0.0

        peak_pos = int(out.argmax())
        peak_value = float(out[peak_pos])
        peak_time = g["timestamp"].iloc[peak_pos]

        restoration_hours = pd.NA
        if peak_value > 0:
            after = g.iloc[peak_pos:]
            recovered = after[after["customers_out"] <= 0.10 * peak_value]
            if not recovered.empty:
                delta = recovered["timestamp"].iloc[0] - peak_time
                restoration_hours = round(delta.total_seconds() / 3600.0, 2)

        rows.append(
            {
                "fips_code": fips,
                "county_name": county,
                "state_name": state,
                "peak_customers_out": int(peak_value),
                "peak_timestamp": peak_time.isoformat(),
                "customer_hours_out": round(customer_hours, 1),
                "restoration_hours_to_10pct": restoration_hours,
            }
        )

    result = pd.DataFrame(rows).sort_values("customer_hours_out", ascending=False)
    result["severity_rank"] = range(1, len(result) + 1)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/ian_florida_outages_2022.csv")
    parser.add_argument("--output", default="data/processed/ian_county_severity.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input, dtype={"fips_code": "string"})
    result = county_severity(df)
    output = ensure_parent_dir(args.output)
    result.to_csv(output, index=False)
    print(f"Counties scored: {len(result):,}")
    print(f"Saved: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
