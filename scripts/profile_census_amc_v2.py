"""Create AMC Census staging table."""
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

    # Filter to AMC wards only
    ward = df[(df["District"] == 474) & (df["Level"] == "WARD")]
    amc = ward[
        ward["Name"].str.contains("M Corp", case=False, na=False)
    ].copy()
    print(f"AMC ward records: {len(amc)}")

    # Key fields
    key_fields = [
        "TOT_P", "TOT_M", "TOT_F",
        "P_06", "M_06", "F_06",
        "P_SC", "M_SC", "F_SC",
        "P_ST", "M_ST", "F_ST",
        "P_LIT", "M_LIT", "F_LIT",
        "P_ILL", "M_ILL", "F_ILL",
        "TOT_WORK_P", "TOT_WORK_M", "TOT_WORK_F",
        "MAINWORK_P", "MAINWORK_M", "MAINWORK_F",
        "MARGWORK_P", "MARGWORK_M", "MARGWORK_F",
        "NON_WORK_P", "NON_WORK_M", "NON_WORK_F",
        "No_HH",
    ]

    # Create staging table
    staging_cols = ["Ward", "Name"] + [
        f for f in key_fields if f in amc.columns
    ]
    staging_df = amc[staging_cols].copy()
    staging_df = staging_df.rename(columns={
        "Ward": "census_ward_id",
        "Name": "ward_name",
    })
    staging_df["source_id"] = "census_2011"
    staging_df["district_code"] = 474
    staging_df["state_code"] = 24

    Path(STAGING_CSV).parent.mkdir(parents=True, exist_ok=True)
    staging_df.to_csv(STAGING_CSV, index=False)
    print(f"Staging table: {STAGING_CSV} ({len(staging_df)} rows)")

    # Demographic summary
    demo = {}
    for field in key_fields:
        if field in amc.columns:
            demo[field] = int(amc[field].sum())

    profile = {
        "dataset_id": "census_ahmedabad_2011",
        "domain": "demographics",
        "source_name": "Census of India 2011",
        "source_type": "PRIMARY_OFFICIAL",
        "source_url": "https://censusindia.gov.in/",
        "source_file": CENSUS_FILE,
        "source_sha256": sha256_file(CENSUS_FILE),
        "acquired_at": "2026-08-30",
        "original_format": "XLSX",
        "transformation_version": "v2.0.0",
        "status": "READY",
        "evidence_classification": "PRIMARY_OFFICIAL",
        "source_status": "VERIFIED",
        "access_status": "PUBLIC",
        "ml_suitability": "PARTIALLY_SUITABLE",
        "sheet_names": ["EB-2407"],
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "amc_ward_count": int(amc["Ward"].nunique()),
        "amc_ward_ids": sorted(amc["Ward"].unique().tolist()),
        "demographic_summary": demo,
        "quality_checks": {
            "duplicate_ward_ids": int(amc["Ward"].duplicated().sum()),
            "missing_ward_ids": int(amc["Ward"].isna().sum()),
            "missing_population": int(amc["TOT_P"].isna().sum()),
        },
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(profile, f, indent=2, default=str)
    print(f"Profile: {OUTPUT_JSON}")

    # Markdown
    d = profile["demographic_summary"]
    md_lines = [
        "# Census 2011 - Ahmedabad AMC Profiling",
        "",
        "**Status**: READY",
        "**Source**: Census of India 2011",
        f"**File**: `{CENSUS_FILE}`",
        f"**SHA256**: `{profile['source_sha256']}`",
        "",
        "## Workbook Structure",
        "",
        f"| Property | Value |",
        f"|----------|-------|",
        f"| Sheet names | {profile['sheet_names']} |",
        f"| Total rows | {profile['total_rows']} |",
        f"| Total columns | {profile['total_columns']} |",
        f"| AMC ward count | {profile['amc_ward_count']} |",
        "",
        "## Key Demographic Fields (AMC Wards Total)",
        "",
        "| Field | Description | Value |",
        "|-------|-------------|-------|",
        f"| TOT_P | Total population | {d.get('TOT_P', 0):,} |",
        f"| TOT_M | Male population | {d.get('TOT_M', 0):,} |",
        f"| TOT_F | Female population | {d.get('TOT_F', 0):,} |",
        f"| P_06 | Child 0-6 | {d.get('P_06', 0):,} |",
        f"| P_LIT | Literate | {d.get('P_LIT', 0):,} |",
        f"| P_ILL | Illiterate | {d.get('P_ILL', 0):,} |",
        f"| TOT_WORK_P | Total workers | {d.get('TOT_WORK_P', 0):,} |",
        f"| NON_WORK_P | Non-workers | {d.get('NON_WORK_P', 0):,} |",
        f"| No_HH | Households | {d.get('No_HH', 0):,} |",
        "",
        "## Quality Checks",
        "",
        f"- Duplicate ward IDs: {profile['quality_checks']['duplicate_ward_ids']}",
        f"- Missing ward IDs: {profile['quality_checks']['missing_ward_ids']}",
        f"- Missing population: {profile['quality_checks']['missing_population']}",
        "",
        "## Known Limitations",
        "",
        "- Census 2011 has 57 AMC wards (2011 delimitation)",
        "- Current GIS has 48 wards (2024 delimitation)",
        "- CROSSWALK REQUIRED between 2011 and 2024 ward boundaries",
    ]

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Markdown: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
