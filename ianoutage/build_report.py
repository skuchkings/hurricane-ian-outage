#!/usr/bin/env python3
"""Generate RESULTS.md directly from the pipeline outputs.

This is the honesty backstop of the project: the headline figures in your
write-up come straight out of the files the pipeline produced, not from anything
typed in by hand. If the inputs are missing, it stops and tells you to run the
pipeline first. It will never invent a number.

Run LAST, after peak_by_county, severity, and restoration_curve.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def require(path: str) -> Path:
    p = Path(path)
    if not p.exists():
        raise SystemExit(
            f"Missing input: {p}\n"
            "Run the pipeline on real data first. This report is built only from "
            "actual pipeline outputs; it does not generate placeholder figures."
        )
    return p


def fmt(n) -> str:
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--peaks", default="data/processed/ian_peak_outages_by_county.csv")
    parser.add_argument("--severity", default="data/processed/ian_county_severity.csv")
    parser.add_argument("--metrics", default="data/processed/ian_florida_restoration_metrics.json")
    parser.add_argument("--output", default="docs/RESULTS.md")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    peaks = pd.read_csv(require(args.peaks))
    severity = pd.read_csv(require(args.severity))
    metrics = json.loads(require(args.metrics).read_text(encoding="utf-8"))

    top_peak = peaks.sort_values("peak_customers_out", ascending=False).head(args.top)
    top_sev = severity.sort_values("customer_hours_out", ascending=False).head(args.top)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Hurricane Ian Florida Outage -- Results",
        "",
        f"_Generated {stamp} from the pipeline outputs listed below. "
        "Every figure here was computed by the scripts, not entered by hand._",
        "",
        f"- Source peak table: `{args.peaks}`",
        f"- Source severity table: `{args.severity}`",
        f"- Source restoration metrics: `{args.metrics}`",
        "",
        "## Statewide",
        "",
        f"- Peak customers without power: **{fmt(metrics.get('state_peak_customers_out'))}**",
        f"- Time of statewide peak: **{metrics.get('state_peak_timestamp')}**",
        f"- First below 50% of peak: {metrics.get('first_time_below_50pct_of_peak')}",
        f"- First below 25% of peak: {metrics.get('first_time_below_25pct_of_peak')}",
        f"- First below 10% of peak: {metrics.get('first_time_below_10pct_of_peak')}",
        f"- First below 5% of peak: {metrics.get('first_time_below_5pct_of_peak')}",
        "",
        f"## Top {args.top} counties by peak customers out",
        "",
        "| Rank | County | Peak customers out | Peak time |",
        "| ---: | --- | ---: | --- |",
    ]
    for _, r in top_peak.iterrows():
        lines.append(
            f"| {fmt(r['peak_rank_statewide'])} | {r['county_name']} | "
            f"{fmt(r['peak_customers_out'])} | {r['peak_timestamp']} |"
        )

    lines += [
        "",
        f"## Top {args.top} counties by customer-hours of outage (duration-weighted)",
        "",
        "| Rank | County | Customer-hours out | Restoration hrs to 10% |",
        "| ---: | --- | ---: | ---: |",
    ]
    for _, r in top_sev.iterrows():
        rest = r["restoration_hours_to_10pct"]
        rest_str = "not reached in window" if pd.isna(rest) else f"{rest}"
        lines.append(
            f"| {fmt(r['severity_rank'])} | {r['county_name']} | "
            f"{fmt(r['customer_hours_out'])} | {rest_str} |"
        )

    lines += [
        "",
        "## Caveat",
        "",
        "EAGLE-I reports utility customers without power, not individual people. "
        "A customer may be a meter, household, or account. Figures are a strong "
        "county-level indicator, not an exact person-level count.",
        "",
    ]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
