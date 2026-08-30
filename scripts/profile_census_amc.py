"""Filter Census to AMC ward-level records and create staging table."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


CENSUS_FILE = "data/raw/census/DDW_PCA2407_2011_MDDS with UI (1).xlsx"
OUTPUT_JSON = "data/profiles/census_ahmedabad_2011.json"
OUTPUT_MD = "data/profiles/census_ahmedabad_2011.md"
STAGING_CSV = "data/staging/census/wards_census_2011_amc.csv"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    df = pd.read_excel(CENSUS_FILE, sheet_name=0)
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    # Ahmedabad district = District code 474
    ahmedabad = df[df["District"] == 474].copy()
    print(f"\nAhmedabad district records: {len(ahmedabad)}")

    # Filter to ward-level: Level == 'WARD' or Ward > 0
    # Check what levels exist
    print(f"Levels in Ahmedabad: {ahmedabad['Level'].unique()}")

    # Ward-level: Level contains 'WARD' or Ward > 0
    ward_mask = (
        ahmedabad["Level"].str.upper().str.contains("WARD", na=False)
        | (ahmedabad["Ward"] > 0)
    )
    ward_records = ahmedabad[ward_mask].copy()
    print(f"Ward-level records: {len(ward_records)}")

    # Also check for Municipal Corporation level
    mc_mask = ahmedabad["Level"].str.upper().str.contains(
        "MUNICIPAL", na=False
    )
    mc_records = ahmedabad[mc_mask].copy()
    print(f"Municipal Corporation records: {len(mc_records)}")

    # Check TRU (Total/Rural/Urban)
    print(f"\nTRU values in ward records: {ward_records['TRU'].unique()}")

    # Filter to Total only for ward-level
    ward_total = ward_records[ward_records["TRU"] == "Total"].copy()
    print(f"Ward Total records: {len(ward_total)}")

    # Profile the ward-level data
    print(f"\nWard IDs: {sorted(ward_total['Ward'].unique())}")
    print(f"Ward count: {ward_total['Ward'].nunique()}")
    print(f"Ward names: {list(ward_total['Name'].head(10))}")

    # Key demographic fields
    key_fields = [
        "TOT_P", "TOT_M", "TOT_F",  # Total population
        "P_06", "M_06", "F_06",  # Child 0-6
        "P_SC", "M_SC", "F_SC",  # SC
        "P_ST", "M_ST", "F_ST",  # ST
        "P_LIT", "M_LIT", "F_LIT",  # Literate
        "P_ILL", "M_ILL", "F_ILL",  # Illiterate
        "TOT_WORK_P", "TOT_WORK_M", "TOT_WORK_F",  # Workers
        "NON_WORK_P", "NON_WORK_M", "NON_WORK_F",  # Non-workers
        "No_HH",  # Households
    ]

    print("\n=== Key Demographic Summary (Ward-level) ===")
    for field in key_fields:
        if field in ward_total.columns:
            total = ward_total[field].sum()
            print(f"  {field}: {total:,.0f}")

    # Create staging table
    staging_cols = ["Ward", "Name", "TRU", "Level"] + key_fields
    staging_df = ward_total[staging_cols].copy()
    staging_df = staging_df.rename(columns={
        "Ward": "census_ward_id",
        "Name": "ward_name",
    })
    staging_df["source_id"] = "census_2011"
    staging_df["district_code"] = 474
    staging_df["state_code"] = 24

    Path(STAGING_CSV).parent.mkdir(parents=True, exist_ok=True)
    staging_df.to_csv(STAGING_CSV, index=False)
    print(f"\nStaging table written to {STAGING_CSV}")
    print(f"Staging rows: {len(staging_df)}")
    print(f"Staging columns: {list(staging_df.columns)}")

    # Create detailed profile
    profile = {
        "dataset_id": "census_ahmedabad_2011",
        "domain": "demographics",
        "source_name": "Census of India 2011",
        "source_type": "PRIMARY_OFFICIAL",
        "source_url": "https://censusindia.gov.in/",
        "source_file": CENSUS_FILE,
        "source_sha256": sha256_file(CENSUS_FILE),
        "acquired_at": "2026-08-30",
        "original_format": "XLSX (Excel)",
        "transformation_version": "v2.0.0",
        "status": "READY",
        "evidence_classification": "PRIMARY_OFFICIAL",
        "source_status": "VERIFIED",
        "access_status": "PUBLIC",
        "ml_suitability": "PARTIALLY_SUITABLE",
        "notes": "Ward-level data for Ahmedabad Municipal Corporation.",
        "sheet_names": ["EB-2407"],
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "ahmedabad_district_records": len(ahmedabad),
        "ward_level_records": len(ward_total),
        "ward_count": int(ward_total["Ward"].nunique()),
        "ward_ids": sorted(ward_total["Ward"].unique().tolist()),
        "columns": list(df.columns),
        "key_fields": key_fields,
        "demographic_summary": {
            field: int(ward_total[field].sum())
            for field in key_fields
            if field in ward_total.columns
        },
        "quality_checks": {
            "duplicate_ward_ids": int(
                ward_total["Ward"].duplicated().sum()
            ),
            "missing_ward_ids": int(ward_total["Ward"].isna().sum()),
            "missing_population": int(ward_total["TOT_P"].isna().sum()),
            "zero_population": int((ward_total["TOT_P"] == 0).sum()),
        },
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(profile, f, indent=2, default=str)
    print(f"\nProfile saved to {OUTPUT_JSON}")

    # Create markdown
    md = f"""# Census 2011 — Ahmedabad AMC Profiling

**Status**: READY
**Source**: Census of India 2011
**File**: `{CENSUS_FILE}`
**SHA256**: `{profile['source_sha256']}`

## Workbook Structure

| Property | Value |
|----------|-------|
| Sheet names | {profile['sheet_names']} |
| Total rows | {profile['total_rows']} |
| Total columns | {profile['total_columns']} |
| Ahmedabad district records | {profile['ahmedabad_district_records']} |
| Ward-level records | {profile['ward_level_records']} |
| Ward count | {profile['ward_count']} |

## Geographic Hierarchy

State (24) → District (474: Ahmadabad) → Subdistt → Town/Village → Ward → EB

## Key Demographic Fields (Ward-level Total)

| Field | Description | Value |
|-------|-------------|-------|
| TOT_P | Total population | {profile['demographic_summary'].get('TOT_P', 'N/A'):,} |
| TOT_M | Male population | {profile['demographic_summary'].get('TOT_M', 'N/A'):,} |
| TOT_F | Female population | {profile['demographic_summary'].get('TOT_F', 'N/A'):,} |
| P_06 | Child population (0-6) | {profile['demographic_summary'].get('P_06', 'N/A'):,} |
| P_LIT | Literate population | {profile['demographic_summary'].get('P_LIT', 'N/A'):,} |
| P_ILL | Illiterate population | {profile['demographic_summary'].get('P_ILL', 'N/A'):,} |
| TOT_WORK_P | Total workers | {profile['demographic_summary'].get('TOT_WORK_P', 'N/A'):,} |
| NON_WORK_P | Non-workers | {profile['demographic_summary'].get('NON_WORK_P', 'N/A'):,} |
| No_HH | Households | {profile['demographic_summary'].get('No_HH', 'N/A'):,} |

## All 94 Columns

{chr(10).join(f'- `{col}`' for col in profile['columns'])}

## Quality Checks

- Duplicate ward IDs: {profile['quality_checks']['duplicate_ward_ids']}
- Missing ward IDs: {profile['quality_checks']['missing_ward_ids']}
- Missing population: {profile['quality_checks']['missing_population']}
- Zero population: {profile['quality_checks']['zero_population']}

## Known Limitations

- Census 2011 has 57 AMC wards (2011 delimitation)
- Current GIS has 48 wards (2024 delimitation)
- **CROSSWALK REQUIRED** between 2011 and 2024 ward boundaries
- No age-group breakdown beyond 0-6
"""
    Path(OUTPUT_MD).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w") as f:
        f.write(md)
    print(f"Markdown saved to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
