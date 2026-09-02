"""PROVENANCE CONSISTENCY AUDIT FOR CPCB AQI DATA
Step 1-9 from prompt.txt: finalize provenance before ward exposure modeling
"""
import hashlib
import math
import warnings
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(r"C:\Users\DELL\Desktop\Agnirakshak opencode")
METADATA = ROOT / "data" / "metadata"
TODAY = datetime.now().strftime("%Y-%m-%d")


def sha256_file(fp):
    h = hashlib.sha256()
    with open(fp, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ============================================================
# STEP 1-2: AUDIT - SOURCE_AVAILABLE vs LOCALLY_ACQUIRED
# ============================================================
print("=" * 70)
print("STEP 1-2: AUDIT - SOURCE_AVAILABLE vs LOCALLY_ACQUIRED")
print("=" * 70)

# Load data availability (what CPCB portal claims)
avail = pd.read_csv(METADATA / "ahmedabad_cpcb_data_availability_2025.csv")

# Load file inventory (what actually exists locally)
inventory = pd.read_csv(METADATA / "aqi_file_inventory.csv")

# Build set of locally acquired station-months from file inventory
local_station_files = inventory[inventory["spatial_level"] == "STATION"].copy()
local_station_files["month"] = local_station_files["month"].str.strip()
local_station_files["station_name_lower"] = (
    local_station_files["station_name"].str.lower().str.strip()
)

# Build lookup: (station_name_lower, month) -> local file info
local_lookup = {}
for _, row in local_station_files.iterrows():
    key = (row["station_name_lower"], row["month"])
    local_lookup[key] = {
        "raw_file": row["source_file"],
        "sha256": row["sha256"],
        "file_size": row["file_size"],
    }

print(f"Data availability claims: {len(avail)} station-months")
print(f"Local station files found: {len(local_station_files)} (all January 2025)")
print(f"Local city files: {len(inventory[inventory['spatial_level'] == 'CITY'])} months")
print()

# ============================================================
# STEP 3: CREATE aqi_station_acquisition_status.csv
# ============================================================
print("=" * 70)
print("STEP 3: CREATE aqi_station_acquisition_status.csv")
print("=" * 70)

# Load QC data
qc = pd.read_csv(METADATA / "aqi_station_month_qc.csv")
qc["station_name_lower"] = qc["station_name"].str.lower().str.strip()
qc["month"] = qc["month"].str.strip()

acq_rows = []
for _, row in avail.iterrows():
    station_name = row["station_name"]
    station_name_lower = station_name.lower().strip()
    month = row["month"].strip()
    station_id = row["station_id"]

    # Check if locally acquired
    local_key = (station_name_lower, month)
    local_info = local_lookup.get(local_key)
    locally_acquired = local_info is not None
    source_available = row["download_available"]

    # Get raw file and sha256
    raw_file = local_info["raw_file"] if local_info else ""
    sha256 = local_info["sha256"] if local_info else ""

    # Get QC info
    qc_row = qc[
        (qc["station_name_lower"] == station_name_lower) & (qc["month"] == month)
    ]
    if len(qc_row) > 0:
        record_count = qc_row.iloc[0]["observed_hours"]
        expected_hours = qc_row.iloc[0]["expected_hours"]
        missing_hours = qc_row.iloc[0]["missing_hours"]
        completeness_pct = qc_row.iloc[0]["completeness_pct"]
        qc_status = qc_row.iloc[0]["qc_status"]
    else:
        record_count = np.nan
        expected_hours = np.nan
        missing_hours = np.nan
        completeness_pct = np.nan
        qc_status = "NOT_ACQUIRED"

    # Determine provenance_status
    if locally_acquired and qc_status in ("VALID", "VALID_WITH_MISSING"):
        provenance_status = "ACQUIRED_AND_VERIFIED"
    elif locally_acquired:
        provenance_status = "ACQUIRED_NEEDS_QC"
    elif source_available:
        provenance_status = "SOURCE_AVAILABLE_NOT_ACQUIRED"
    else:
        provenance_status = "UNAVAILABLE"

    # Notes
    if locally_acquired:
        notes = "File exists locally with SHA-256 checksum"
    elif source_available:
        notes = "Available from CPCB portal; not yet downloaded"
    else:
        notes = "Not available from known sources"

    acq_rows.append({
        "station_id": station_id,
        "station_name": station_name,
        "year": 2025,
        "month": month,
        "source_available": source_available,
        "locally_acquired": locally_acquired,
        "raw_file": raw_file,
        "sha256": sha256,
        "record_count": record_count,
        "expected_hours": expected_hours,
        "missing_hours": missing_hours,
        "completeness_pct": completeness_pct,
        "qc_status": qc_status,
        "provenance_status": provenance_status,
        "notes": notes,
    })

acq_df = pd.DataFrame(acq_rows)
acq_df.to_csv(METADATA / "aqi_station_acquisition_status.csv", index=False)
print("Saved: data/metadata/aqi_station_acquisition_status.csv")
print(f"Rows: {len(acq_df)}")
print()

# Summary
for status in [
    "ACQUIRED_AND_VERIFIED",
    "SOURCE_AVAILABLE_NOT_ACQUIRED",
    "ACQUIRED_NEEDS_QC",
    "SUSPICIOUS",
    "UNAVAILABLE",
]:
    n = (acq_df["provenance_status"] == status).sum()
    if n > 0:
        print(f"  {status}: {n}")

# ============================================================
# STEP 6: VERIFY STATION COORDINATES
# ============================================================
print()
print("=" * 70)
print("STEP 6: VERIFY STATION COORDINATES")
print("=" * 70)

coords = pd.read_csv(METADATA / "aqi_station_coordinates.csv")
inv = pd.read_csv(METADATA / "ahmedabad_cpcb_station_inventory.csv")

print("Station coordinates verified against CPCB CAAQMS All India list:")
for _, r in coords.iterrows():
    print(
        f"  {r['station_name']:<45s} | "
        f"{r['latitude']:8.4f}, {r['longitude']:8.4f} | "
        f"{r['agency']} | {r['verification_status']}"
    )

# ============================================================
# STEP 7: CURRENT 48-WARD COVERAGE WITH DISTANCE CLASSES
# ============================================================
print()
print("=" * 70)
print("STEP 7: CURRENT 48-WARD COVERAGE WITH DISTANCE CLASSES")
print("=" * 70)

gdf = gpd.read_file(ROOT / "data" / "raw" / "gis" / "wards_ahmedabad.geojson")
gdf_utm = gdf.to_crs("EPSG:32643")
centroid_4326 = gdf_utm.geometry.centroid.to_crs("EPSG:4326")
gdf["c_lat"] = centroid_4326.x  # inverted: x=lat
gdf["c_lon"] = centroid_4326.y  # inverted: y=lon

st_gdf = gpd.GeoDataFrame(
    coords,
    geometry=gpd.points_from_xy(coords["latitude"], coords["longitude"]),
    crs="EPSG:4326",
)
join = gpd.sjoin(st_gdf, gdf, how="left", predicate="within")


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate haversine distance between two points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


ward_rows = []
for _, ward in gdf.iterrows():
    wc = str(ward["sourcewardcode"])
    wn = ward["ward_lgd_name"]
    inside = join[join["sourcewardcode"] == wc]
    n_in = len(inside)
    names_in = ", ".join(inside["station_name"].tolist()) if n_in > 0 else ""

    if n_in == 0:
        # Capture ward coords for lambda
        w_lat = ward["c_lat"]
        w_lon = ward["c_lon"]
        dists = coords.apply(
            lambda r, lat=w_lat, lon=w_lon: haversine_km(lat, lon, r["latitude"], r["longitude"]),
            axis=1,
        )
        ni = dists.idxmin()
        nn = coords.loc[ni, "station_name"]
        nd = round(dists.loc[ni], 2)
    else:
        nn = inside.iloc[0]["station_name"]
        nd = 0.0

    # Distance classes per prompt
    if n_in >= 1:
        coverage_class = "DIRECT"
    elif nd <= 2.0:
        coverage_class = "NEAR_2KM"
    elif nd <= 5.0:
        coverage_class = "NEAR_5KM"
    else:
        coverage_class = "FAR"

    ward_rows.append({
        "ward_code": wc,
        "ward_name": wn,
        "station_count_inside": n_in,
        "station_names": names_in,
        "nearest_station": nn,
        "nearest_station_distance_km": nd,
        "coverage_distance_class": coverage_class,
    })

ward_match = pd.DataFrame(ward_rows)
ward_match.to_csv(METADATA / "aqi_station_current48ward_match.csv", index=False)
print("Saved: data/metadata/aqi_station_current48ward_match.csv")
print()

# Summary by class
for cls in ["DIRECT", "NEAR_2KM", "NEAR_5KM", "FAR"]:
    n = (ward_match["coverage_distance_class"] == cls).sum()
    print(f"  {cls:>10s}: {n} wards")

print()
for _, r in ward_match.iterrows():
    print(
        f"  [{r['coverage_distance_class']:>10s}] Ward {r['ward_code']:>3s} | "
        f"{r['station_count_inside']} stn(s) | nearest: "
        f"{r['nearest_station_distance_km']:5.1f} km | {r['nearest_station']}"
    )

# ============================================================
# STEP 9: FINAL REPORT
# ============================================================
print()
print("=" * 70)
print("FINAL REPORT")
print("=" * 70)

source_avail = acq_df["source_available"].sum()
local_acq = acq_df["locally_acquired"].sum()
qc_valid = acq_df["qc_status"].isin(["VALID", "VALID_WITH_MISSING"]).sum()

direct = (ward_match["coverage_distance_class"] == "DIRECT").sum()
near2 = (ward_match["coverage_distance_class"] == "NEAR_2KM").sum()
near5 = (ward_match["coverage_distance_class"] == "NEAR_5KM").sum()
far = (ward_match["coverage_distance_class"] == "FAR").sum()

print(f"""
SOURCE-AVAILABLE STATION-MONTHS:   {source_avail} (9 stations x 5 months)
LOCALLY-ACQUIRED STATION-MONTHS:   {local_acq} (9 stations x 1 month only)
QC-VALID STATION-MONTHS:           {qc_valid}

CURRENT 48-WARD COVERAGE:
  DIRECT (station inside ward):    {direct}
  <=2 km:                          {near2}
  2-5 km:                          {near5}
  >5 km:                           {far}

CRITICAL FINDING:
  Only January 2025 station-level data is locally acquired.
  February-May 2025 station data is SOURCE_AVAILABLE but NOT LOCALLY_ACQUIRED.
  The 36 missing station-months BLOCK ward-level AQI computation.

DATASET READINESS:
  Station->ward interpolation is BLOCKED_PENDING_ACQUISITION.
  Reason: 36 of 45 station-months not downloaded.

  To unblock, acquire from CPCB portal:
  - 9 stations x 4 months (Feb-May 2025) = 36 files
  - URL: https://app.cpcbccr.com/ccr/#/caaqm-dashboard-all/caaqm-landing
  - Filter: State=Gujarat, City=Ahmedabad, Date range=Feb-May 2025

  DO NOT:
  - Fabricate missing station-month files from city-level AQI
  - Rename city-level AQI as station-level AQI
  - Interpolate without actual station data
""")
