#!/usr/bin/env python3
"""Download the 2022 Census cartographic county boundary shapefile."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import requests

from ianoutage.config import CENSUS_COUNTY_2022_500K_URL
from ianoutage.utils import ensure_parent_dir


def download_file(url: str, output: Path) -> None:
    ensure_parent_dir(output)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with output.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\rDownloading {output.name}: {pct:5.1f}%", end="")
    print()


def validate_zip(path: Path) -> None:
    if not zipfile.is_zipfile(path):
        raise ValueError(f"Downloaded file is not a valid zip: {path}")
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
    expected = [".shp", ".dbf", ".shx", ".prj"]
    missing = [ext for ext in expected if not any(name.endswith(ext) for name in names)]
    if missing:
        raise ValueError(f"Zip file is missing required shapefile components: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=CENSUS_COUNTY_2022_500K_URL)
    parser.add_argument("--output", default="data/raw/cb_2022_us_county_500k.zip")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output = Path(args.output)
    if output.exists() and not args.force:
        print(f"Already exists: {output}")
        validate_zip(output)
        return 0

    print(f"Source: {args.url}")
    download_file(args.url, output)
    validate_zip(output)
    print(f"Saved: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
