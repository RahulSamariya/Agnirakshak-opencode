"""Generate updated provenance manifest with SHA256 hashes."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import xarray as xr


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_provenance() -> dict:
    now = datetime.now(UTC).isoformat()
    manifest = {
        "generated_at": now,
        "schema_version": "v2.0.0",
        "hash_algorithm": "SHA256",
        "datasets": {},
    }

    # ERA5-Land
    nc_path = "data/raw/weather/data_0.nc"
    if Path(nc_path).exists():
        ds = xr.open_dataset(nc_path)
        manifest["datasets"]["era5land"] = {
            "dataset_id": "era5land_ahmedabad_2010_03",
            "domain": "weather",
            "source_name": "ERA5-Land (Copernicus)",
            "source_type": "PRIMARY_OFFICIAL",
            "source_url": "https://cds.climate.copernicus.eu/",
            "source_file": nc_path,
            "source_sha256": sha256_file(nc_path),
            "acquired_at": now,
            "original_format": "NetCDF (CF-1.6)",
            "transformation_version": "v2.0.0",
            "status": "READY",
            "evidence_classification": "PRIMARY_OFFICIAL",
            "source_status": "VERIFIED",
            "access_status": "PUBLIC",
            "ml_suitability": "PARTIALLY_SUITABLE",
            "file_size_bytes": Path(nc_path).stat().st_size,
            "dimensions": dict(ds.sizes),
            "variables": list(ds.data_vars),
            "time_range": [str(ds.valid_time.values.min()), str(ds.valid_time.values.max())],
            "latitude_range": [float(ds.latitude.min()), float(ds.latitude.max())],
            "longitude_range": [float(ds.longitude.min()), float(ds.longitude.max())],
            "notes": "March 2010 sample only.",
        }
        ds.close()

    # GIS (raw)
    geojson_path = "data/raw/gis/wards_ahmedabad.geojson"
    if Path(geojson_path).exists():
        manifest["datasets"]["gis_raw"] = {
            "dataset_id": "gis_ahmedabad_wards_2024",
            "domain": "geospatial",
            "source_name": "Ahmedabad Municipal Corporation",
            "source_type": "PRIMARY_OFFICIAL",
            "source_url": None,
            "source_file": geojson_path,
            "source_sha256": sha256_file(geojson_path),
            "acquired_at": now,
            "original_format": "GeoJSON",
            "transformation_version": "v2.0.0",
            "status": "READY",
            "evidence_classification": "PRIMARY_OFFICIAL",
            "source_status": "VERIFIED",
            "access_status": "PUBLIC",
            "ml_suitability": "PARTIALLY_SUITABLE",
            "file_size_bytes": Path(geojson_path).stat().st_size,
            "feature_count": 48,
            "crs": "EPSG:4326",
            "coordinate_order": "latitude_longitude",
            "notes": "48 wards (2024 delimitation). Coordinate order is lat/lon.",
        }

    # GIS (normalized)
    staging_path = "data/staging/gis/wards_ahmedabad_epsg4326_normalized.geojson"
    if Path(staging_path).exists():
        manifest["datasets"]["gis_normalized"] = {
            "dataset_id": "gis_ahmedabad_normalized",
            "domain": "geospatial",
            "source_name": "Ahmedabad Municipal Corporation (normalized)",
            "source_type": "PRIMARY_OFFICIAL",
            "source_file": staging_path,
            "source_sha256": sha256_file(staging_path),
            "acquired_at": now,
            "original_format": "GeoJSON",
            "transformation_version": "v2.0.0",
            "status": "READY",
            "transformation": "Coordinate swap from lat/lon to lon/lat per GeoJSON spec",
            "original_coordinate_order": "latitude_longitude",
            "normalized_coordinate_order": "longitude_latitude",
            "original_hash": sha256_file(geojson_path),
            "notes": "Normalized copy with [lon, lat] coordinate order.",
        }

    # AQI
    aqi_dir = Path("data/raw/aqi")
    aqi_files = sorted(aqi_dir.glob("*.xlsx"))
    if aqi_files:
        aqi_manifest = {
            "dataset_id": "cpcb_ahmedabad_2025_01_05",
            "domain": "air_quality",
            "source_name": "Central Pollution Control Board (CPCB)",
            "source_type": "PRIMARY_OFFICIAL",
            "source_url": "https://cpcb.gov.in/",
            "source_files": [],
            "acquired_at": now,
            "original_format": "XLSX",
            "transformation_version": "v2.0.0",
            "status": "PARTIAL",
            "evidence_classification": "PRIMARY_OFFICIAL",
            "source_status": "VERIFIED",
            "access_status": "PUBLIC",
            "ml_suitability": "PARTIALLY_SUITABLE",
            "file_count": len(aqi_files),
            "notes": "City-level AQI. ~5% missing values.",
        }
        for f in aqi_files:
            aqi_manifest["source_files"].append({
                "file": f.name,
                "sha256": sha256_file(str(f)),
                "size_bytes": f.stat().st_size,
            })
        manifest["datasets"]["aqi"] = aqi_manifest

    # Census
    census_path = "data/raw/census/DDW_PCA2407_2011_MDDS with UI (1).xlsx"
    if Path(census_path).exists():
        manifest["datasets"]["census"] = {
            "dataset_id": "census_ahmedabad_2011",
            "domain": "demographics",
            "source_name": "Census of India 2011",
            "source_type": "PRIMARY_OFFICIAL",
            "source_url": "https://censusindia.gov.in/",
            "source_file": census_path,
            "source_sha256": sha256_file(census_path),
            "acquired_at": now,
            "original_format": "XLSX",
            "transformation_version": "v2.0.0",
            "status": "READY",
            "evidence_classification": "PRIMARY_OFFICIAL",
            "source_status": "VERIFIED",
            "access_status": "PUBLIC",
            "ml_suitability": "PARTIALLY_SUITABLE",
            "file_size_bytes": Path(census_path).stat().st_size,
            "amc_ward_count": 57,
            "notes": "57 AMC wards profiled.",
        }
    else:
        manifest["datasets"]["census"] = {
            "dataset_id": "census_ahmedabad_2011",
            "domain": "demographics",
            "source_name": "Census of India 2011",
            "source_type": "PRIMARY_OFFICIAL",
            "source_url": "https://censusindia.gov.in/",
            "source_file": census_path,
            "source_sha256": None,
            "acquired_at": None,
            "original_format": "XLSX",
            "transformation_version": None,
            "status": "BLOCKED",
            "evidence_classification": "PRIMARY_OFFICIAL",
            "source_status": "UNAVAILABLE",
            "access_status": "UNAVAILABLE",
            "ml_suitability": "UNKNOWN",
            "notes": "File not found.",
        }

    return manifest


def main():
    manifest = build_provenance()
    output_path = "data/metadata/provenance-manifest.json"
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"Provenance manifest written to {output_path}")
    print(f"Datasets documented: {len(manifest['datasets'])}")
    for name, info in manifest["datasets"].items():
        status = info.get("status", "N/A")
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()
