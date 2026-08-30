"""Census 2011 profiling script for Ahmedabad AMC.

Run after placing DDW_PCA2407_2011_MDDS with UI (1).xlsx in data/raw/census/.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


CENSUS_FILE = "data/raw/census/DDW_PCA2407_2011_MDDS with UI (1).xlsx"
OUTPUT_JSON = "data/profiles/census_ahmedabad_2011.json"
OUTPUT_MD = "data/profiles/census_ahmedabad_2011.md"
STAGING_DIR = Path("data/staging/census")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def profile_census() -> dict:
    if not Path(CENSUS_FILE).exists():
        print(f"ERROR: Census file not found: {CENSUS_FILE}")
        return {"status": "BLOCKED", "notes": "File not found"}

    print(f"Loading {CENSUS_FILE}...")
    xl = pd.ExcelFile(CENSUS_FILE)
    sheet_names = xl.sheet_names
    print(f"Sheet names: {sheet_names}")

    # Load first sheet (typically the main data)
    df = pd.read_excel(CENSUS_FILE, sheet_name=0)
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Profile
    profile = {
        "sheet_names": sheet_names,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "sha256": sha256_file(CENSUS_FILE),
    }

    # Look for Ahmedabad AMC records
    # Common patterns: district name contains "Ahmedabad", town type is "Municipal Corporation"
    for col in df.columns:
        col_lower = str(col).lower()
        if "district" in col_lower or "dist" in col_lower:
            unique_vals = df[col].dropna().unique()
            print(f"\nColumn '{col}' unique values (first 20): {list(unique_vals[:20])}")
            ahmedabad_mask = df[col].astype(str).str.contains("Ahmedabad", case=False, na=False)
            amc_count = ahmedabad_mask.sum()
            print(f"Ahmedabad records in '{col}': {amc_count}")
            profile["ahmedabad_column"] = col
            profile["ahmedabad_record_count"] = int(amc_count)

        if "ward" in col_lower or "ward" in str(col).lower():
            print(f"Ward column found: '{col}'")
            print(f"  Unique values: {df[col].nunique()}")
            print(f"  Sample: {list(df[col].head(10))}")
            profile["ward_column"] = col
            profile["ward_count"] = int(df[col].nunique())

    return profile


def main():
    profile = profile_census()

    if profile.get("status") == "BLOCKED":
        print("\nCensus profiling BLOCKED — file not available")
        return

    # Save JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(profile, f, indent=2, default=str)
    print(f"\nProfile saved to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
