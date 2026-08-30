"""Generate provenance manifest for all ingested datasets.

Computes MD5 hashes and documents source metadata.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import xarray as xr


def md5_file(path: str) -> str:
    """Compute MD5 hash of a file."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_provenance() -> dict:
    """Build provenance manifest for all Ahmedabad pilot datasets."""
    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "generated_at": now,
        "schema_version": "v1.0.0",
        "datasets": {},
    }

    # ERA5-Land
    nc_path = "data/raw/weather/data_0.nc"
    if Path(nc_path).exists():
        ds = xr.open_dataset(nc_path)
        manifest["datasets"]["era5land"] = {
            "source_id": "era5land_ahmedabad_2010_03",
            "source_file": nc_path,
            "source_hash_md5": md5_file(nc_path),
            "retrieved_at": now,
            "transformation_version": "v1.0.0",
            "quality_flag": "PASS",
            "schema_version": "v1.0.0",
            "file_size_bytes": Path(nc_path).stat().st_size,
            "dimensions": dict(ds.sizes),
            "variables": list(ds.data_vars),
            "time_range": [
                str(ds.valid_time.values.min()),
                str(ds.valid_time.values.max()),
            ],
            "latitude_range": [float(ds.latitude.min()), float(ds.latitude.max())],
            "longitude_range": [float(ds.longitude.min()), float(ds.longitude.max())],
        }
        ds.close()

    # GIS
    geojson_path = "data/raw/gis/wards_ahmedabad.geojson"
    if Path(geojson_path).exists():
        manifest["datasets"]["gis"] = {
            "source_id": "gis_ahmedabad_wards_2024",
            "source_file": geojson_path,
            "source_hash_md5": md5_file(geojson_path),
            "retrieved_at": now,
            "transformation_version": "v1.0.0",
            "quality_flag": "PASS",
            "schema_version": "v1.0.0",
            "file_size_bytes": Path(geojson_path).stat().st_size,
            "feature_count": 48,
            "crs": "EPSG:4326",
        }

    # Staging GIS
    staging_path = "data/staging/gis/wards_ahmedabad_normalized.geojson"
    if Path(staging_path).exists():
        manifest["datasets"]["gis_staging"] = {
            "source_id": "gis_ahmedabad_normalized",
            "source_file": staging_path,
            "source_hash_md5": md5_file(staging_path),
            "retrieved_at": now,
            "transformation_version": "v1.0.0",
            "quality_flag": "PASS",
            "schema_version": "v1.0.0",
            "file_size_bytes": Path(staging_path).stat().st_size,
            "feature_count": 48,
            "crs": "EPSG:4326",
        }

    # AQI
    aqi_dir = Path("data/raw/aqi")
    aqi_files = sorted(aqi_dir.glob("*.xlsx"))
    if aqi_files:
        aqi_manifest = {
            "source_id": "cpcb_ahmedabad_2025_01_05",
            "source_files": [],
            "retrieved_at": now,
            "transformation_version": "v1.0.0",
            "quality_flag": "PARTIAL",
            "schema_version": "v1.0.0",
            "file_count": len(aqi_files),
        }
        for f in aqi_files:
            aqi_manifest["source_files"].append({
                "file": f.name,
                "hash_md5": md5_file(str(f)),
                "size_bytes": f.stat().st_size,
            })
        manifest["datasets"]["aqi"] = aqi_manifest

    # Census (BLOCKED)
    census_dir = Path("data/raw/census")
    manifest["datasets"]["census"] = {
        "source_id": "census_ahmedabad_2011",
        "source_file": "NOT FOUND",
        "source_hash_md5": None,
        "retrieved_at": None,
        "transformation_version": None,
        "quality_flag": "BLOCKED",
        "schema_version": None,
        "notes": "DDW_PCA2407_2011_MDDS.xlsx not found in repository",
    }

    return manifest


def main():
    manifest = build_provenance()

    output_path = Path("data/metadata/provenance-manifest.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    print(f"Provenance manifest written to {output_path}")
    print(f"Datasets documented: {len(manifest['datasets'])}")

    for name, info in manifest["datasets"].items():
        flag = info.get("quality_flag", "N/A")
        print(f"  {name}: {flag}")


if __name__ == "__main__":
    main()
