"""Census 2011 profiling — inspect actual workbook."""
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
    xl = pd.ExcelFile(CENSUS_FILE)
    print(f"Sheet names: {xl.sheet_names}")

    # Load first sheet
    df = pd.read_excel(CENSUS_FILE, sheet_name=0)
    print(f"Shape: {df.shape}")
    print(f"Columns ({len(df.columns)}): {list(df.columns)}")

    # Print first 5 rows
    print("\nFirst 5 rows:")
    print(df.head().to_string())

    # Look for Ahmedabad
    ahmedabad_records = pd.DataFrame()
    ward_col = None
    for col in df.columns:
        col_str = str(col).lower()
        if "district" in col_str or "dist" in col_str:
            mask = df[col].astype(str).str.contains(
                "Ahmedabad", case=False, na=False
            )
            count = mask.sum()
            if count > 0:
                print(f"\nAhmedabad in '{col}': {count} records")
                ahmedabad_records = df[mask]

        if "ward" in col_str and ward_col is None:
            ward_col = col
            print(f"Ward column: '{col}' unique={df[col].nunique()}")

    # Profile Ahemdabad records
    if len(ahmedabad_records) > 0:
        print(f"\n=== Ahmedabad Records: {len(ahmedabad_records)} ===")
        print(f"Columns: {list(ahmedabad_records.columns)}")

        # Numeric columns
        numeric_cols = ahmedabad_records.select_dtypes(
            include=["int64", "float64"]
        ).columns
        print(f"\nNumeric columns: {list(numeric_cols)}")

        for col in numeric_cols[:20]:
            vals = ahmedabad_records[col].dropna()
            if len(vals) > 0:
                print(
                    f"  {col}: min={vals.min()}, max={vals.max()}, "
                    f"mean={vals.mean():.1f}"
                )

        # Check for ward-level data
        if ward_col:
            print(f"\nWard-level records: {len(ahmedabad_records)}")
            print(f"Unique wards: {ahmedabad_records[ward_col].nunique()}")
            print(f"Sample ward IDs: {list(ahmedabad_records[ward_col].head(10))}")

    return {
        "sheet_names": xl.sheet_names,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "ahmedabad_record_count": len(ahmedabad_records),
        "ward_column": ward_col,
        "sha256": sha256_file(CENSUS_FILE),
    }


def main():
    profile = profile_census()

    Path(OUTPUT_JSON).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(profile, f, indent=2, default=str)
    print(f"\nProfile saved to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
