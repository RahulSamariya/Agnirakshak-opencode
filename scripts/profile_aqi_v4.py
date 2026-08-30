"""Enhanced AQI profiling with SHA256 and staging table creation."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

AQI_DIR = "data/raw/aqi"
OUTPUT_JSON = "data/profiles/aqi_ahmedabad_2025_v2.json"
OUTPUT_MD = "docs/data/aqi_ahmedabad_2025_v2.md"
STAGING_CSV = "data/staging/aqi/aqi_ahmedabad_2025_normalized.csv"

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3,
    "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9,
    "October": 10, "November": 11, "December": 12,
}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_month_from_filename(filename: str) -> int | None:
    for name, num in MONTH_MAP.items():
        if name in filename:
            return num
    return None


def profile_aqi() -> dict:
    aqi_files = sorted(Path(AQI_DIR).glob("*.xlsx"))
    print(f"Found {len(aqi_files)} AQI files")

    monthly_profiles = []
    all_records = []

    for f in aqi_files:
        print(f"\nProcessing: {f.name}")
        month = extract_month_from_filename(f.name)
        year = 2025

        df = pd.read_excel(f)
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")

        # Melt to long format
        id_vars = ["Date"]
        hourly_cols = [c for c in df.columns if c != "Date"]
        melted = df.melt(id_vars=id_vars, value_vars=hourly_cols,
                         var_name="Hour", value_name="AQI")

        # Create timestamps
        melted["Date_str"] = melted["Date"].astype(str)
        melted["timestamp"] = pd.to_datetime(
            melted["Date_str"] + " " + melted["Hour"],
            errors="coerce"
        )

        # Quality analysis
        total_cells = len(melted)
        missing_aqi = int(melted["AQI"].isnull().sum())
        valid_aqi = total_cells - missing_aqi

        # Duplicate check
        has_ts = "timestamp" in melted.columns
        dup_count = int(melted.duplicated(subset=["timestamp"]).sum()) if has_ts else 0

        # AQI statistics
        aqi_min = float(melted["AQI"].min()) if valid_aqi > 0 else None
        aqi_max = float(melted["AQI"].max()) if valid_aqi > 0 else None
        aqi_mean = float(melted["AQI"].mean()) if valid_aqi > 0 else None

        monthly_profiles.append({
            "file": f.name,
            "month": month,
            "year": year,
            "sha256": sha256_file(str(f)),
            "rows": len(df),
            "columns": list(df.columns),
            "total_cells": total_cells,
            "valid_cells": valid_aqi,
            "missing_cells": missing_aqi,
            "missing_pct": round(missing_aqi / total_cells * 100, 2) if total_cells > 0 else 0,
            "duplicate_timestamps": dup_count,
            "aqi_min": aqi_min,
            "aqi_max": aqi_max,
            "aqi_mean": aqi_mean,
            "hourly_columns": hourly_cols,
        })

        # Collect records for staging table
        for _, row in melted.iterrows():
            all_records.append({
                "timestamp": row["timestamp"],
                "location_id": "ahmedabad_city",
                "aqi": row["AQI"],
                "source_id": f"cpcb_ahmedabad_2025_{month:02d}",
                "quality_flag": "MISSING" if pd.isna(row["AQI"]) else "VALID",
                "month": month,
                "year": year,
            })

    total_records = len(all_records)

    def _is_missing(val):
        if val is None:
            return True
        if isinstance(val, float) and pd.isna(val):
            return True
        return False

    total_missing = sum(1 for r in all_records if _is_missing(r["aqi"]))

    profile = {
        "dataset_id": "cpcb_ahmedabad_2025_01_05",
        "domain": "air_quality",
        "source_name": "Central Pollution Control Board (CPCB)",
        "source_type": "PRIMARY_OFFICIAL",
        "source_url": "https://cpcb.gov.in/",
        "source_file": AQI_DIR,
        "source_sha256": None,
        "acquired_at": datetime.now(UTC).isoformat(),
        "original_format": "XLSX (Excel)",
        "transformation_version": "v2.0.0",
        "status": "PARTIAL",
        "evidence_classification": "PRIMARY_OFFICIAL",
        "source_status": "VERIFIED",
        "access_status": "PUBLIC",
        "ml_suitability": "PARTIALLY_SUITABLE",
        "notes": "City-level AQI only. No station-level breakdown. ~5% missing values.",
        "file_count": len(aqi_files),
        "monthly_profiles": monthly_profiles,
        "total_records": total_records,
        "total_missing": total_missing,
        "overall_missing_pct": (
            round(total_missing / total_records * 100, 2)
            if total_records > 0 else 0
        ),
        "date_range": {
            "start": "2025-01-01",
            "end": "2025-05-31",
        },
        "city": "Ahmedabad",
        "frequency": "hourly",
        "aqi_scale": "CPCB National Air Quality Index (NAQI)",
        "has_station_metadata": False,
        "has_pollutant_columns": False,
    }

    return profile, all_records


def create_staging_table(records: list[dict]) -> None:
    """Create normalized staging CSV."""
    df = pd.DataFrame(records)
    Path(STAGING_CSV).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(STAGING_CSV, index=False)
    print(f"Staging table written to {STAGING_CSV} ({len(df)} rows)")


def write_markdown(profile: dict) -> None:
    md_lines = [
        "# AQI Ahmedabad 2025 — Enhanced Profile v2",
        "",
        f"**Status**: {profile['status']}",
        f"**Source**: {profile['source_name']}",
        f"**City**: {profile['city']}",
        f"**Frequency**: {profile['frequency']}",
        f"**Date range**: {profile['date_range']['start']} to {profile['date_range']['end']}",
        "",
        "## Monthly Summary",
        "",
        "| Month | File | Rows | Valid | Missing | Min | Max | Mean |",
        "|-------|------|------|-------|---------|-----|-----|------|",
    ]

    for mp in profile["monthly_profiles"]:
        month_name = list(MONTH_MAP.keys())[list(MONTH_MAP.values()).index(mp["month"])]
        md_lines.append(
            f"| {month_name} | {mp['file'][:30]}... | {mp['rows']} | "
            f"{mp['valid_cells']} | {mp['missing_cells']} ({mp['missing_pct']}%) | "
            f"{mp['aqi_min']:.0f} | {mp['aqi_max']:.0f} | {mp['aqi_mean']:.1f} |"
        )

    md_lines += [
        "",
        "## Overall",
        "",
        f"- Total records: {profile['total_records']}",
        f"- Total missing: {profile['total_missing']}",
        f"- Overall missing %: {profile['overall_missing_pct']}%",
        "",
        "## Known Limitations",
        "",
        "- City-level average only (no station breakdown)",
        "- No pollutant breakdown columns",
        "- ~5% missing values across all months",
        "- Date column contains day numbers (1-31), month encoded in filename",
        "",
    ]

    Path(OUTPUT_MD).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md_lines))
    print(f"Markdown written to {OUTPUT_MD}")


def main():
    print("Profiling AQI...")
    profile, records = profile_aqi()

    Path(OUTPUT_JSON).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(profile, f, indent=2, default=str)
    print(f"\nJSON written to {OUTPUT_JSON}")

    write_markdown(profile)
    create_staging_table(records)
    print("Done.")


if __name__ == "__main__":
    main()
