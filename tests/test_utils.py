import pandas as pd

from ianoutage.utils import clean_column_name, standardize_fips
from ianoutage.severity import county_severity
from ianoutage.validate import run_checks


def test_clean_column_name():
    assert clean_column_name("Customers Without Power") == "customers_without_power"
    assert clean_column_name(" FIPS Code ") == "fips_code"


def test_standardize_fips_preserves_leading_zeros():
    values = pd.Series([12071, "12015", "12021.0", " 12115 ", 6037])
    assert standardize_fips(values).tolist() == ["12071", "12015", "12021", "12115", "06037"]


def _toy_frame():
    # One county, rising then recovering. Peak 100 at hour 1; back to <=10 at hour 3.
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2022-09-28 00:00",
                    "2022-09-28 01:00",
                    "2022-09-28 02:00",
                    "2022-09-28 03:00",
                ]
            ),
            "fips_code": ["12071"] * 4,
            "county_name": ["Lee"] * 4,
            "state_name": ["Florida"] * 4,
            "customers_out": [20, 100, 40, 5],
        }
    )


def test_severity_metrics():
    out = county_severity(_toy_frame())
    row = out.iloc[0]
    assert row["peak_customers_out"] == 100
    # Trapezoidal area over 3 hours: (20+100)/2 + (100+40)/2 + (40+5)/2 = 152.5
    assert abs(row["customer_hours_out"] - 152.5) < 1e-6
    # Peak at hour 1, first <=10 (which is 5) at hour 3 => 2 hours.
    assert float(row["restoration_hours_to_10pct"]) == 2.0


def test_validate_flags_negative(tmp_path):
    slice_csv = tmp_path / "slice.csv"
    peaks_csv = tmp_path / "peaks.csv"
    _toy_frame().assign(customers_out=[-1, 100, 40, 5]).to_csv(slice_csv, index=False)
    pd.DataFrame(
        {
            "fips_code": ["12071"],
            "county_name": ["Lee"],
            "peak_customers_out": [100],
            "peak_rank_statewide": [1],
        }
    ).to_csv(peaks_csv, index=False)
    failures, _ = run_checks(str(slice_csv), str(peaks_csv), ceiling=4_000_000)
    assert any("negative" in f for f in failures)
