"""AHMEDABAD STATION AQI INGEST + QC PIPELINE
Steps 1-12 from prompt.txt
"""
import hashlib
import os
import json
import warnings
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

ROOT = Path(r"C:\Users\DELL\Desktop\Agnirakshak opencode")
RAW_STATION = ROOT  # station xlsx files are in root
RAW_CITY = ROOT / "data" / "raw" / "aqi"
STAGING = ROOT / "data" / "staging" / "aqi"
CURATED = ROOT / "data" / "curated" / "aqi"
METADATA = ROOT / "data" / "metadata"
PROFILES = ROOT / "data" / "profiles"

for d in [STAGING, CURATED, METADATA]:
    d.mkdir(parents=True, exist_ok=True)

# QC thresholds (configurable)
VALID_THRESHOLD = 0.95
VALID_WITH_MISSING_THRESHOLD = 0.80

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# ============================================================
# STEP 1: INVENTORY ALL AQI FILES
# ============================================================
print("=" * 70)
print("STEP 1: INVENTORY ALL AQI FILES")
print("=" * 70)

inventory = []

# Station-level files in root
for f in sorted(RAW_STATION.glob("aqi_hourly_station_level_*.xlsx")):
    fname = f.name
    # Parse: aqi_hourly_station_level_<station>,_<city>_-_<agency>_<year>_<month>_<city>_<year>.xlsx
    parts = fname.replace(".xlsx", "").split("_")
    # Extract station name from filename
    station_part = fname.replace("aqi_hourly_station_level_", "").replace("_ahmedabad_", "|").replace("_iitm_2025", "|").replace("_gpcb_2025", "|")
    station_raw = fname.replace("aqi_hourly_station_level_", "").split("_-_")[0].replace("_", " ").replace(",", ",")
    agency = "IITM" if "iitm" in fname.lower() else "GPCB" if "gpcb" in fname.lower() else "UNKNOWN"
    
    # Better parsing
    base = fname.replace("aqi_hourly_station_level_", "").replace(".xlsx", "")
    if "_-_iitm_" in base:
        station_name = base.split("_-_iitm_")[0].replace("_", " ").replace(",", ",")
        agency = "IITM"
        month_year = base.split("_-_iitm_")[1]  # e.g. "2025_January_ahmedabad_2025"
    elif "_-_gpcb_" in base:
        station_name = base.split("_-_gpcb_")[0].replace("_", " ").replace(",", ",")
        agency = "GPCB"
        month_year = base.split("_-_gpcb_")[1]
    else:
        station_name = base.split("_-_")[0].replace("_", " ") if "_-_" in base else base.replace("_", " ")
        agency = "UNKNOWN"
        month_year = ""
    
    # Parse month from month_year
    month_str = month_year.split("_")[1] if len(month_year.split("_")) > 1 else "unknown"
    year_str = "2025"
    
    inventory.append({
        "source_file": fname,
        "station_name": station_name.strip(),
        "agency": agency,
        "year": year_str,
        "month": month_str,
        "file_size": f.stat().st_size,
        "sha256": sha256_file(f),
        "spatial_level": "STATION",
        "path": str(f),
    })

# City-level files
for f in sorted(RAW_CITY.glob("aqi_hourly_city_level_*.xlsx")):
    fname = f.name
    # e.g. aqi_hourly_city_level__2025_January_ahmedabad_2025.xlsx
    base = fname.replace("aqi_hourly_city_level__", "").replace(".xlsx", "")
    parts = base.split("_")
    year_str = parts[0] if len(parts) > 0 else "unknown"
    month_str = parts[1] if len(parts) > 1 else "unknown"
    
    inventory.append({
        "source_file": fname,
        "station_name": "Ahmedabad City",
        "agency": "CPCB",
        "year": year_str,
        "month": month_str,
        "file_size": f.stat().st_size,
        "sha256": sha256_file(f),
        "spatial_level": "CITY",
        "path": str(f),
    })

print(f"\nFound {len(inventory)} files:")
for inv in inventory:
    print(f"  [{inv['spatial_level']:5}] {inv['station_name']:45} | {inv['agency']:4} | {inv['month']:10} | {inv['sha256'][:16]}...")

# Save inventory
inv_df = pd.DataFrame(inventory)
inv_df.to_csv(METADATA / "aqi_file_inventory.csv", index=False)
print(f"\nSaved: {METADATA / 'aqi_file_inventory.csv'}")

# ============================================================
# STEP 2: NORMALIZE HOURLY DATA (wide → long)
# ============================================================
print("\n" + "=" * 70)
print("STEP 2: NORMALIZE HOURLY DATA")
print("=" * 70)

all_records = []

for inv in inventory:
    fpath = Path(inv["path"])
    spatial_level = inv["spatial_level"]
    
    try:
        df = pd.read_excel(fpath, engine="openpyxl")
    except Exception as e:
        print(f"  ERROR reading {fpath.name}: {e}")
        continue
    
    # Identify date column and hour columns
    date_col = None
    hour_cols = []
    for col in df.columns:
        col_str = str(col).strip().lower()
        if col_str in ("date", "日期", "time", "datetime", "timestamp"):
            date_col = col
        elif ":" in str(col):
            hour_cols.append(col)
    
    if date_col is None:
        # Try first column as date
        date_col = df.columns[0]
        hour_cols = [c for c in df.columns[1:] if ":" in str(c)]
    
    if not hour_cols:
        print(f"  WARNING: No hour columns found in {fpath.name}. Columns: {list(df.columns)[:10]}")
        continue
    
    print(f"  Processing {inv['station_name']:40} | {inv['month']:10} | {len(df)} days × {len(hour_cols)} hours")
    
    records = []
    for _, row in df.iterrows():
        date_val = row[date_col]
        if pd.isna(date_val):
            continue
        try:
            if isinstance(date_val, str):
                dt = pd.to_datetime(date_val)
            else:
                dt = pd.to_datetime(date_val)
        except:
            continue
        
        for hc in hour_cols:
            hour_str = str(hc).strip()
            try:
                hour = int(hour_str.split(":")[0])
            except:
                continue
            
            ts = dt.replace(hour=hour)
            aqi_val = row[hc]
            
            # Convert to numeric, preserve NaN
            try:
                aqi_num = float(aqi_val) if not pd.isna(aqi_val) else np.nan
            except:
                aqi_num = np.nan
            
            records.append({
                "station_name": inv["station_name"],
                "agency": inv["agency"],
                "spatial_level": spatial_level,
                "timestamp_local": ts,
                "aqi": aqi_num,
                "source_file": inv["source_file"],
                "year": inv["year"],
                "month": inv["month"],
            })
    
    all_records.extend(records)

# Combine all records
df_all = pd.DataFrame(all_records)
if len(df_all) > 0:
    df_all = df_all.sort_values(["station_name", "timestamp_local"]).reset_index(drop=True)

print(f"\nTotal records: {len(df_all)}")
print(f"Station-level records: {(df_all['spatial_level'] == 'STATION').sum()}")
print(f"City-level records: {(df_all['spatial_level'] == 'CITY').sum()}")
print(f"Distinct stations: {df_all['station_name'].nunique()}")

# ============================================================
# STEP 3: STATION-MONTH QC
# ============================================================
print("\n" + "=" * 70)
print("STEP 3: STATION-MONTH QC")
print("=" * 70)

qc_rows = []
for (station, year, month), grp in df_all.groupby(["station_name", "year", "month"]):
    n = len(grp)
    aqi_vals = grp["aqi"].dropna()
    n_valid = len(aqi_vals)
    n_missing = n - n_valid
    
    # Expected hours in month
    month_map = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5,
                 "June": 6, "July": 7, "August": 8, "September": 9, "October": 10,
                 "November": 11, "December": 12}
    m = month_map.get(month, 1)
    expected = 24 * pd.Timestamp(year=int(year), month=m, day=1).days_in_month
    
    completeness = n_valid / expected if expected > 0 else 0
    
    # Gap analysis
    if len(grp) > 1:
        grp_sorted = grp.sort_values("timestamp_local")
        ts_diff = grp_sorted["timestamp_local"].diff().dt.total_seconds() / 3600
        max_gap = int(ts_diff.max()) if len(ts_diff) > 0 else 0
        # Count consecutive missing
        gaps = []
        current_gap = 0
        for _, r in grp_sorted.iterrows():
            if pd.isna(r["aqi"]):
                current_gap += 1
            else:
                if current_gap > 0:
                    gaps.append(current_gap)
                current_gap = 0
        if current_gap > 0:
            gaps.append(current_gap)
        max_consecutive_missing = max(gaps) if gaps else 0
    else:
        max_gap = 0
        max_consecutive_missing = 0
    
    qc_rows.append({
        "station_name": station,
        "year": year,
        "month": month,
        "expected_hours": expected,
        "observed_hours": n_valid,
        "missing_hours": n_missing,
        "completeness_pct": round(completeness * 100, 1),
        "min_aqi": round(aqi_vals.min(), 1) if len(aqi_vals) > 0 else np.nan,
        "max_aqi": round(aqi_vals.max(), 1) if len(aqi_vals) > 0 else np.nan,
        "mean_aqi": round(aqi_vals.mean(), 1) if len(aqi_vals) > 0 else np.nan,
        "median_aqi": round(aqi_vals.median(), 1) if len(aqi_vals) > 0 else np.nan,
        "p95_aqi": round(aqi_vals.quantile(0.95), 1) if len(aqi_vals) > 0 else np.nan,
        "max_consecutive_missing_hours": max_consecutive_missing,
        "max_gap_length_hours": max_gap,
    })

qc_df = pd.DataFrame(qc_rows)
print(qc_df.to_string(index=False))

# ============================================================
# STEP 4: QA FLAGS
# ============================================================
print("\n" + "=" * 70)
print("STEP 4: QA FLAGS")
print("=" * 70)

def assign_qa_status(row):
    comp = row["completeness_pct"] / 100.0
    if comp >= VALID_THRESHOLD:
        if row["missing_hours"] == 0:
            return "VALID"
        return "VALID_WITH_MISSING"
    elif comp >= VALID_WITH_MISSING_THRESHOLD:
        return "VALID_WITH_MISSING"
    elif comp > 0:
        return "QUARANTINED"
    else:
        return "INVALID"

qc_df["qc_status"] = qc_df.apply(assign_qa_status, axis=1)

for status in ["VALID", "VALID_WITH_MISSING", "QUARANTINED", "INVALID"]:
    n = (qc_df["qc_status"] == status).sum()
    if n > 0:
        stations = qc_df[qc_df["qc_status"] == status]["station_name"].tolist()
        print(f"  {status:20}: {n} station-months — {stations}")

qc_df.to_csv(METADATA / "aqi_station_month_qc.csv", index=False)
print(f"\nSaved: {METADATA / 'aqi_station_month_qc.csv'}")

# ============================================================
# STEP 5: DUPLICATE/SERIES CONSISTENCY CHECK
# ============================================================
print("\n" + "=" * 70)
print("STEP 5: DUPLICATE/SERIES CONSISTENCY CHECK")
print("=" * 70)

# Check if any station appears with duplicate month entries
dup_check = df_all.groupby(["station_name", "year", "month", "timestamp_local"])["aqi"].count().reset_index()
dup_check.columns = ["station_name", "year", "month", "timestamp_local", "count"]
dups = dup_check[dup_check["count"] > 1]

if len(dups) > 0:
    print(f"  Found {len(dups)} duplicate timestamp entries:")
    print(dups.head(10).to_string(index=False))
else:
    print("  No duplicate timestamps found across station-months.")

# Check for near-duplicate series (same station, same timestamps from different source files)
print("\n  Checking for accidental file duplication...")
for station in df_all["station_name"].unique():
    sdf = df_all[df_all["station_name"] == station]
    files = sdf["source_file"].unique()
    if len(files) > 1:
        print(f"  WARNING: {station} has multiple source files: {files}")

# ============================================================
# STEP 6: DO NOT CONFUSE CITY AQI WITH STATION AQI
# ============================================================
print("\n" + "=" * 70)
print("STEP 6: SPATIAL LEVEL SEPARATION")
print("=" * 70)

station_df = df_all[df_all["spatial_level"] == "STATION"].copy()
city_df = df_all[df_all["spatial_level"] == "CITY"].copy()

print(f"  Station-level records: {len(station_df)}")
print(f"  City-level records: {len(city_df)}")
print(f"  Station spatial_level verified: {(station_df['spatial_level'] == 'STATION').all()}")
print(f"  City spatial_level verified: {(city_df['spatial_level'] == 'CITY').all()}")

# ============================================================
# STEP 7: BUILD STATION METADATA
# ============================================================
print("\n" + "=" * 70)
print("STEP 7: BUILD STATION METADATA")
print("=" * 70)

meta_rows = []
for station, grp in station_df.groupby("station_name"):
    agency = grp["agency"].iloc[0]
    n = len(grp)
    expected_total = 0
    for (yr, mo), mg in grp.groupby(["year", "month"]):
        month_map = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5}
        m = month_map.get(mo, 1)
        expected_total += 24 * pd.Timestamp(year=int(yr), month=m, day=1).days_in_month
    
    meta_rows.append({
        "station_name": station,
        "agency": agency,
        "latitude": np.nan,
        "longitude": np.nan,
        "spatial_level": "STATION",
        "source": f"{agency} Ahmedabad 2025",
        "source_url": "",
        "year": "2025",
        "available_months": ", ".join(sorted(grp["month"].unique())),
        "temporal_resolution": "hourly",
        "aqi_available": True,
        "record_count": n,
        "expected_record_count": expected_total,
        "completeness_pct": round(n / expected_total * 100, 1) if expected_total > 0 else 0,
        "qc_status": "",
        "sha256": "",
    })

meta_df = pd.DataFrame(meta_rows)
meta_df.to_csv(METADATA / "aqi_station_metadata.csv", index=False)
print(f"  Stations: {len(meta_df)}")
for _, r in meta_df.iterrows():
    print(f"    {r['station_name']:45} | {r['agency']:4} | {r['available_months']:30} | {r['record_count']:6} records | {r['completeness_pct']:.1f}%")

# ============================================================
# SAVE CLEAN OUTPUTS (Step 12 early)
# ============================================================
print("\n" + "=" * 70)
print("STEP 12: SAVE CLEAN OUTPUTS")
print("=" * 70)

# Save station-level hourly data
out_station = station_df[["station_name", "agency", "timestamp_local", "aqi", "source_file", "year", "month"]].copy()
out_station.to_parquet(CURATED / "ahmedabad_station_hourly_2025.parquet", index=False)
print(f"  Saved: {CURATED / 'ahmedabad_station_hourly_2025.parquet'} ({len(out_station)} records)")

# Save city-level separately
if len(city_df) > 0:
    out_city = city_df[["station_name", "agency", "timestamp_local", "aqi", "source_file", "year", "month"]].copy()
    out_city.to_parquet(CURATED / "ahmedabad_city_hourly_2025.parquet", index=False)
    print(f"  Saved: {CURATED / 'ahmedabad_city_hourly_2025.parquet'} ({len(out_city)} records)")

# Save normalized long-format CSV
df_all.to_csv(STAGING / "aqi_ahmedabad_2025_station_normalized.csv", index=False)
print(f"  Saved: {STAGING / 'aqi_ahmedabad_2025_station_normalized.csv'} ({len(df_all)} records)")

# ============================================================
# FINAL REPORT (Step 15)
# ============================================================
print("\n" + "=" * 70)
print("FINAL REPORT")
print("=" * 70)

total_stations = station_df["station_name"].nunique()
total_sm = len(qc_df)
valid_sm = (qc_df["qc_status"] == "VALID").sum()
valid_missing_sm = (qc_df["qc_status"] == "VALID_WITH_MISSING").sum()
quarantined_sm = (qc_df["qc_status"] == "QUARANTINED").sum()
invalid_sm = (qc_df["qc_status"] == "INVALID").sum()
total_records = len(station_df)
total_missing = station_df["aqi"].isna().sum()
total_expected = qc_df["expected_hours"].sum()
overall_completeness = (total_records - total_missing) / total_expected * 100 if total_expected > 0 else 0

print(f"""
TOTAL DISTINCT STATIONS:        {total_stations}
TOTAL STATION-MONTHS:           {total_sm}
  VALID:                        {valid_sm}
  VALID_WITH_MISSING:           {valid_missing_sm}
  QUARANTINED:                  {quarantined_sm}
  INVALID:                      {invalid_sm}
TOTAL HOURLY RECORDS:           {total_records}
TOTAL MISSING RECORDS:          {total_missing}
OVERALL COMPLETENESS:           {overall_completeness:.1f}%

STATION LIST:""")
for _, r in meta_df.iterrows():
    print(f"  {r['station_name']:45} | {r['agency']:4} | {r['record_count']:6} records | {r['completeness_pct']:.1f}%")

print(f"""
NOTE: Station coordinates (latitude, longitude) are NOT YET VERIFIED.
      Prompt requires authoritative CPCB/GPCB coordinates.
      Ward coverage assessment (Steps 8-11) deferred to separate script
      once coordinates are verified.
""")
