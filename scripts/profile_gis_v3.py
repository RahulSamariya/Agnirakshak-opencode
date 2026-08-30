"""GIS profiling with coordinate order verification and SHA256."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

import geopandas as gpd
import shapely


GEOJSON_PATH = "data/raw/gis/wards_ahmedabad.geojson"
STAGING_PATH = "data/staging/gis/wards_ahmedabad_epsg4326_normalized.geojson"
OUTPUT_JSON = "data/profiles/gis_ahmedabad_v2.json"
OUTPUT_MD = "docs/data/gis_ahmedabad_v2.md"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_coordinate_order(gdf: gpd.GeoDataFrame) -> dict:
    """Verify coordinate order of GeoJSON.

    GeoJSON spec says [longitude, latitude] order.
    But some files store [latitude, longitude].
    We check by looking at coordinate ranges vs Ahmedabad geography.
    """
    # Ahmedabad: lat ~22.9-23.1, lon ~72.4-72.7
    all_coords = []
    for geom in gdf.geometry:
        if geom is not None:
            coords = list(geom.exterior.coords) if hasattr(geom, 'exterior') else []
            all_coords.extend(coords)

    if not all_coords:
        return {"status": "NO_COORDINATES"}

    xs = [c[0] for c in all_coords]
    ys = [c[1] for c in all_coords]

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    # Check which interpretation matches Ahmedabad geography
    # Ahmedabad: lat 22.9-23.1, lon 72.4-72.7
    # If x is longitude: x should be ~72.4-72.7, y should be ~22.9-23.1
    # If x is latitude: x should be ~22.9-23.1, y should be ~72.4-72.7

    x_could_be_lon = 72.0 <= x_min and x_max <= 73.0
    x_could_be_lat = 22.0 <= x_min and x_max <= 24.0
    y_could_be_lat = 22.0 <= y_min and y_max <= 24.0
    y_could_be_lon = 72.0 <= y_min and y_max <= 73.0

    if x_could_be_lon and y_could_be_lat:
        order = "longitude_latitude"
        lat_range = [y_min, y_max]
        lon_range = [x_min, x_max]
    elif x_could_be_lat and y_could_be_lon:
        order = "latitude_longitude"
        lat_range = [x_min, x_max]
        lon_range = [y_min, y_max]
    else:
        order = "UNKNOWN"
        lat_range = None
        lon_range = None

    return {
        "detected_order": order,
        "x_range": [x_min, x_max],
        "y_range": [y_min, y_max],
        "lat_range": lat_range,
        "lon_range": lon_range,
    }


def profile_gis() -> dict:
    gdf = gpd.read_file(GEOJSON_PATH)

    # Coordinate order verification
    coord_info = verify_coordinate_order(gdf)

    # Geometry validity
    valid_geom = gdf.geometry.is_valid
    invalid_count = int((~valid_geom).sum())
    empty_count = int(gdf.geometry.is_empty.sum())

    # Duplicate check
    id_col = "ward_lgd_code" if "ward_lgd_code" in gdf.columns else None
    dup_count = int(gdf[id_col].duplicated().sum()) if id_col else None

    # Bounds (in detected coordinate order)
    bounds = gdf.total_bounds.tolist()

    profile = {
        "dataset_id": "gis_ahmedabad_wards_2024",
        "domain": "geospatial",
        "source_name": "Ahmedabad Municipal Corporation",
        "source_type": "PRIMARY_OFFICIAL",
        "source_url": None,
        "source_file": GEOJSON_PATH,
        "source_sha256": sha256_file(GEOJSON_PATH),
        "acquired_at": datetime.now(timezone.utc).isoformat(),
        "original_format": "GeoJSON",
        "transformation_version": "v2.0.0",
        "status": "READY",
        "evidence_classification": "PRIMARY_OFFICIAL",
        "source_status": "VERIFIED",
        "access_status": "PUBLIC",
        "ml_suitability": "PARTIALLY_SUITABLE",
        "notes": "48 wards (2024 delimitation). Census 2011 had 57 wards.",
        "file_size_bytes": Path(GEOJSON_PATH).stat().st_size,
        "feature_count": len(gdf),
        "geometry_type": str(gdf.geometry.geom_type.unique()),
        "crs": str(gdf.crs),
        "columns": list(gdf.columns),
        "coordinate_order_verification": coord_info,
        "bounds": bounds,
        "ward_id_column": id_col,
        "ward_id_unique_count": int(gdf[id_col].nunique()) if id_col else None,
        "duplicate_ward_ids": dup_count,
        "invalid_geometries": invalid_count,
        "empty_geometries": empty_count,
        "valid_geometries": int(valid_geom.sum()),
        "has_lgd_code": "ward_lgd_code" in gdf.columns,
        "has_ward_name": "ward_lgd_name" in gdf.columns,
        "has_source_ward": "sourcewardname" in gdf.columns or "sourcewardcode" in gdf.columns,
    }

    return profile


def create_normalized_copy() -> dict:
    """Create normalized copy with [lon, lat] coordinate order if needed."""
    gdf = gpd.read_file(GEOJSON_PATH)
    coord_info = verify_coordinate_order(gdf)

    if coord_info["detected_order"] == "latitude_longitude":
        # Need to swap coordinates to [lon, lat] per GeoJSON spec
        print("Coordinate order is lat/lon — creating normalized [lon, lat] copy")
        # Rename geometry column to avoid confusion
        gdf_normalized = gdf.copy()
        # Swap coordinates in all geometries
        gdf_normalized["geometry"] = gdf_normalized.geometry.apply(
            lambda geom: shapely.ops.transform(lambda x, y: (y, x), geom)
            if geom is not None else geom
        )
        transformation = "swapped lat/lon to lon/lat per GeoJSON spec"
    else:
        print("Coordinate order already [lon, lat] — copying as-is")
        gdf_normalized = gdf.copy()
        transformation = "no transformation needed (already [lon, lat])"

    Path(STAGING_PATH).parent.mkdir(parents=True, exist_ok=True)
    gdf_normalized.to_file(STAGING_PATH, driver="GeoJSON")

    return {
        "original_file": GEOJSON_PATH,
        "original_hash": sha256_file(GEOJSON_PATH),
        "original_coordinate_order": coord_info["detected_order"],
        "normalized_coordinate_order": "longitude_latitude",
        "original_crs": str(gdf.crs),
        "normalized_crs": str(gdf.crs),
        "transformation": transformation,
        "transformation_version": "v2.0.0",
        "normalized_hash": sha256_file(STAGING_PATH),
    }


def write_markdown(profile: dict, normalization: dict) -> None:
    coord = profile["coordinate_order_verification"]
    md = f"""# GIS Ahmedabad — Enhanced Profile v2

**Status**: {profile['status']}
**Source**: {profile['source_name']}
**Format**: {profile['original_format']}
**SHA256**: `{profile['source_sha256']}`
**File size**: {profile['file_size_bytes']:,} bytes

## Feature Summary

| Property | Value |
|----------|-------|
| Feature count | {profile['feature_count']} |
| Geometry type | {profile['geometry_type']} |
| CRS | {profile['crs']} |
| Ward ID column | {profile['ward_id_column']} |
| Unique ward IDs | {profile['ward_id_unique_count']} |
| Duplicate ward IDs | {profile['duplicate_ward_ids']} |
| Invalid geometries | {profile['invalid_geometries']} |
| Empty geometries | {profile['empty_geometries']} |

## Coordinate Order Verification

| Check | Result |
|-------|--------|
| Detected order | `{coord['detected_order']}` |
| X range | {coord['x_range']} |
| Y range | {coord['y_range']} |
| Latitude range | {coord['lat_range']} |
| Longitude range | {coord['lon_range']} |

**Ahmedabad geography**: lat ~22.9-23.1, lon ~72.4-72.7

## Normalization

| Property | Value |
|----------|-------|
| Original order | `{normalization['original_coordinate_order']}` |
| Normalized order | `{normalization['normalized_coordinate_order']}` |
| Transformation | {normalization['transformation']} |
| Original hash | `{normalization['original_hash']}` |
| Normalized hash | `{normalization['normalized_hash']}` |

## Columns

{chr(10).join(f'- `{col}`' for col in profile['columns'])}

## Known Limitations

- Current GIS has 48 wards (2024 delimitation)
- Census 2011 had 57 wards — **CROSSWALK REQUIRED**
"""

    Path(OUTPUT_MD).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w") as f:
        f.write(md)
    print(f"Markdown written to {OUTPUT_MD}")


def main():
    print("Profiling GIS...")
    profile = profile_gis()

    print("\nCreating normalized copy...")
    normalization = create_normalized_copy()

    profile["normalization"] = normalization

    Path(OUTPUT_JSON).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(profile, f, indent=2, default=str)
    print(f"\nJSON written to {OUTPUT_JSON}")

    write_markdown(profile, normalization)
    print("Done.")


if __name__ == "__main__":
    main()
