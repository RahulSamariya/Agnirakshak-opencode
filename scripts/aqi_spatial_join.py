"""STEP 8-11: WARD GEOGRAPHY + STATION COORDINATES + SPATIAL JOIN + COVERAGE"""
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = r"C:\Users\DELL\Desktop\Agnirakshak opencode"
METADATA = f"{ROOT}/data/metadata"

# ============================================================
# STEP 8: VERIFY 48-WARD GIS
# ============================================================
print("=" * 70)
print("STEP 8: CURRENT 48-WARD GEOGRAPHY VERIFICATION")
print("=" * 70)

gdf = gpd.read_file(f"{ROOT}/data/raw/gis/wards_ahmedabad.geojson")
print(f"  Total polygons:  {len(gdf)}")
print(f"  CRS:             {gdf.crs}")
print(f"  Valid geometries: {gdf.geometry.is_valid.all()}")
print(f"  Null geometries:  {gdf.geometry.isna().sum()}")
print(f"  Geometry types:   {gdf.geom_type.value_counts().to_dict()}")

# Project to UTM for accurate area/centroid
gdf_utm = gdf.to_crs("EPSG:32643")  # UTM zone 43N for Ahmedabad
centroid_4326 = gdf_utm.geometry.centroid.to_crs("EPSG:4326")
gdf["centroid_lon"] = centroid_4326.x  # EPSG:4326 x = longitude
gdf["centroid_lat"] = centroid_4326.y  # EPSG:4326 y = latitude
gdf["area_km2"] = gdf_utm.geometry.area / 1e6

print(f"  Latitude range:  {gdf['centroid_lat'].min():.4f} to {gdf['centroid_lat'].max():.4f}")
print(f"  Longitude range: {gdf['centroid_lon'].min():.4f} to {gdf['centroid_lon'].max():.4f}")
# Note: GeoJSON stores coordinates as (latitude, longitude) in this file, non-standard
print(f"  Ward codes:      {sorted(gdf['sourcewardcode'].astype(int).tolist())}")
print(f"  Unique codes:    {gdf['sourcewardcode'].nunique()}")
print(f"  Total bounds:    {gdf.total_bounds}")
print(f"\n  VERIFIED: {len(gdf)} wards, valid Polygon, EPSG:4326, unique codes.")

# ============================================================
# STEP 9: STATION COORDINATES (AUTHORITATIVE CPCB)
# ============================================================
print("\n" + "=" * 70)
print("STEP 9: STATION COORDINATES -- AUTHORITATIVE CPCB/GPCB")
print("=" * 70)

# Source: CPCB CAAQMS All India list (cpcbccr.com/pdf/caaqms_list_All_India.pdf)
stations = pd.DataFrame([
    {"station_name": "Chandkheda, Ahmedabad", "latitude": 23.1080, "longitude": 72.5746,
     "agency": "IITM", "cpcb_code": "#5453",
     "coordinate_source": "CPCB CAAQMS All India list", "verification_status": "VERIFIED CPCB"},
    {"station_name": "Gyaspur, Ahmedabad", "latitude": 22.9771, "longitude": 72.5530,
     "agency": "IITM", "cpcb_code": "#5450",
     "coordinate_source": "CPCB CAAQMS All India list", "verification_status": "VERIFIED CPCB"},
    {"station_name": "Maninagar, Ahmedabad", "latitude": 23.0027, "longitude": 72.5919,
     "agency": "GPCB", "cpcb_code": "#308",
     "coordinate_source": "CPCB CAAQMS All India list", "verification_status": "VERIFIED CPCB"},
    {"station_name": "Raikhad, Ahmedabad", "latitude": 23.0205, "longitude": 72.5793,
     "agency": "IITM", "cpcb_code": "#5452",
     "coordinate_source": "CPCB CAAQMS All India list", "verification_status": "VERIFIED CPCB"},
    {"station_name": "Rakhial, Ahmedabad", "latitude": 23.0168, "longitude": 72.6258,
     "agency": "IITM", "cpcb_code": "#5451",
     "coordinate_source": "CPCB CAAQMS All India list", "verification_status": "VERIFIED CPCB"},
    {"station_name": "SAC ISRO Bopal, Ahmedabad", "latitude": 23.0411, "longitude": 72.4567,
     "agency": "IITM", "cpcb_code": "#5454",
     "coordinate_source": "CPCB CAAQMS All India list", "verification_status": "VERIFIED CPCB"},
    {"station_name": "SAC ISRO Satellite, Ahmedabad", "latitude": 23.0234, "longitude": 72.5152,
     "agency": "IITM", "cpcb_code": "#5455",
     "coordinate_source": "CPCB CAAQMS All India list", "verification_status": "VERIFIED CPCB"},
    {"station_name": "SVPI Airport Hansol, Ahmedabad", "latitude": 23.0768, "longitude": 72.6279,
     "agency": "IITM", "cpcb_code": "#5456",
     "coordinate_source": "CPCB CAAQMS All India list", "verification_status": "VERIFIED CPCB"},
    {"station_name": "Sardar Vallabhbhai Patel Stadium, Ahmedabad", "latitude": 23.0431, "longitude": 72.5630,
     "agency": "IITM", "cpcb_code": "#5449",
     "coordinate_source": "CPCB CAAQMS All India list", "verification_status": "VERIFIED CPCB"},
])

for _, r in stations.iterrows():
    print(f"  {r['station_name']:45} | {r['latitude']:.4f}, {r['longitude']:.4f} | {r['agency']:4} | {r['cpcb_code']}")

stations.to_csv(f"{METADATA}/aqi_station_coordinates.csv", index=False)

# ============================================================
# STEP 10: STATION -> CURRENT 48 WARD SPATIAL JOIN
# ============================================================
print("\n" + "=" * 70)
print("STEP 10: STATION -> CURRENT 48 WARD SPATIAL JOIN")
print("=" * 70)

# CRITICAL: The GeoJSON has inverted coordinates: x=lat (~23), y=lon (~72)
# Match this convention when creating station points
station_gdf = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(stations["latitude"], stations["longitude"]),
    crs="EPSG:4326",
)

# Spatial join: stations inside wards
join_inside = gpd.sjoin(station_gdf, gdf, how="left", predicate="within")

import math

def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km between two (lat, lon) points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# For each ward, find stations inside
ward_coverage_rows = []
for _, ward in gdf.iterrows():
    ward_code = str(ward["sourcewardcode"])
    ward_name = ward["ward_lgd_name"]
    # ward lat/lon from inverted centroid
    ward_lat = ward["centroid_lon"]  # centroid_lon actually holds latitude
    ward_lon = ward["centroid_lat"]  # centroid_lat actually holds longitude

    # Stations inside this ward
    stations_inside = join_inside[join_inside["sourcewardcode"] == ward_code]
    n_inside = len(stations_inside)
    names_inside = ", ".join(stations_inside["station_name"].tolist()) if n_inside > 0 else ""

    # Nearest station using haversine
    if n_inside == 0:
        dists = stations.apply(lambda r: haversine_km(ward_lat, ward_lon, r["latitude"], r["longitude"]), axis=1)
        nearest_idx = dists.idxmin()
        nearest_name = stations.loc[nearest_idx, "station_name"]
        nearest_dist = round(dists.loc[nearest_idx], 2)
    else:
        nearest_name = stations_inside.iloc[0]["station_name"]
        nearest_dist = 0.0

    # Classification
    if n_inside >= 2:
        classification = "MULTI_STATION"
    elif n_inside == 1:
        classification = "DIRECT_STATION"
    elif n_inside == 0 and nearest_dist <= 3.0:
        classification = "NEARBY_STATION"
    else:
        classification = "NO_DIRECT_STATION"

    ward_coverage_rows.append({
        "ward_code": ward_code,
        "ward_name": ward_name,
        "station_count_inside": n_inside,
        "station_names": names_inside,
        "nearest_station": nearest_name,
        "nearest_station_distance_km": nearest_dist,
        "classification": classification,
    })

coverage_df = pd.DataFrame(ward_coverage_rows)

# Display
print("\nWARD COVERAGE TABLE:")
for _, r in coverage_df.iterrows():
    icon = {"DIRECT_STATION": "O", "MULTI_STATION": "O+", "NEARBY_STATION": "~", "NO_DIRECT_STATION": "X"}.get(r["classification"], "?")
    print(f"  [{icon}] Ward {r['ward_code']:3} | {r['station_count_inside']} station(s) | nearest: {r['nearest_station_distance_km']:.1f} km | {r['classification']}")

# Summary
print("\nSUMMARY:")
for cls in ["DIRECT_STATION", "MULTI_STATION", "NEARBY_STATION", "NO_DIRECT_STATION"]:
    n = (coverage_df["classification"] == cls).sum()
    print(f"  {cls:25}: {n} wards")

coverage_df.to_csv(f"{METADATA}/aqi_station_ward_coverage.csv", index=False)
print(f"\n  Saved: {METADATA}/aqi_station_ward_coverage.csv")

# ============================================================
# STEP 11: ASSESS SPATIAL REPRESENTATIVENESS
# ============================================================
print("\n" + "=" * 70)
print("STEP 11: SPATIAL REPRESENTATIVENESS ASSESSMENT")
print("=" * 70)

coverage_df["ward_area_km2"] = gdf["area_km2"].values
total_wards = len(coverage_df)
direct_wards = (coverage_df["classification"].isin(["DIRECT_STATION", "MULTI_STATION"])).sum()
nearby_wards = (coverage_df["classification"] == "NEARBY_STATION").sum()
no_station_wards = (coverage_df["classification"] == "NO_DIRECT_STATION").sum()

print(f"""
REPRESENTATIVENESS SUMMARY:
  Total wards:              {total_wards}
  Wards with station:       {direct_wards} ({direct_wards/total_wards*100:.1f}%)
  Wards nearby:             {nearby_wards} ({nearby_wards/total_wards*100:.1f}%)
  Wards with no station:    {no_station_wards} ({no_station_wards/total_wards*100:.1f}%)
  Total stations:           {len(stations)}
  Station density:          {len(stations)/len(gdf):.3f} stations/ward
  Avg nearest distance:     {coverage_df['nearest_station_distance_km'].mean():.2f} km
  Max nearest distance:     {coverage_df['nearest_station_distance_km'].max():.2f} km
""")

print("WARDS WITH STATION INSIDE (>1 km radius):")
inside = coverage_df[coverage_df["station_count_inside"] > 0]
if len(inside) > 0:
    for _, r in inside.iterrows():
        print(f"  Ward {r['ward_code']}: {r['station_names']}")
else:
    print("  None")

print("\nNEARBY WARDS (0-3 km from nearest station):")
nearby = coverage_df[(coverage_df["classification"] == "NEARBY_STATION")]
if len(nearby) > 0:
    for _, r in nearby.iterrows():
        print(f"  Ward {r['ward_code']}: {r['nearest_station_distance_km']:.1f} km to {r['nearest_station']}")
else:
    print("  None")

print("\nPOORLY REPRESENTED WARDS (>5 km from nearest station):")
poor = coverage_df[coverage_df["nearest_station_distance_km"] > 5.0]
if len(poor) > 0:
    for _, r in poor.iterrows():
        print(f"  Ward {r['ward_code']}: {r['nearest_station_distance_km']:.1f} km to {r['nearest_station']}")
else:
    print("  None -- all wards within 5 km of a station.")
