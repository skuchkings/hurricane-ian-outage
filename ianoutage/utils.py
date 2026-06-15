from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pandas as pd


TIMESTAMP_ALIASES = [
    "timestamp",
    "date_time",
    "datetime",
    "date",
    "time",
    "recorded_at",
    "run_start_time",
    "outage_time",
]
FIPS_ALIASES = [
    "fips_code",
    "fips",
    "county_fips",
    "countyfips",
    "geoid",
    "county_geoid",
]
COUNTY_ALIASES = ["county_name", "county", "countyname"]
STATE_ALIASES = ["state_name", "state", "statename"]
CUSTOMERS_OUT_ALIASES = [
    "customers_out",
    "customers_without_power",
    "customers_out_of_power",
    "customers_outage",
    "outages",
    "outage_count",
    "sum",
]


def clean_column_name(name: str) -> str:
    """Normalize a raw CSV header to a predictable snake_case name."""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized column names."""
    df = df.copy()
    df.columns = [clean_column_name(c) for c in df.columns]
    return df


def first_existing(columns: Iterable[str], aliases: list[str], label: str) -> str:
    columns = list(columns)
    for alias in aliases:
        if alias in columns:
            return alias
    raise ValueError(
        f"Could not find a {label} column. Available columns: {columns}. "
        f"Expected one of: {aliases}"
    )


def standardize_fips(series: pd.Series) -> pd.Series:
    """Convert FIPS values to five-character strings, preserving leading zeros."""
    s = series.astype("string").str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)
    s = s.str.replace(r"[^0-9]", "", regex=True)
    return s.str.zfill(5)


def ensure_parent_dir(path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def safe_to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)
