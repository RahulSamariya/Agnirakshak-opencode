"""Enhanced ERA5-Land profiling with SHA256 and detailed variable documentation."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import xarray as xr

NC_PATH = "data/raw/weather/data_0.nc"
OUTPUT_JSON = "data/profiles/era5land_ahmedabad_v2.json"
OUTPUT_MD = "docs/data/era5land_ahmedabad_v2.md"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def profile_era5() -> dict:
    ds = xr.open_dataset(NC_PATH)

    # Variable documentation
    var_docs = {
        "t2m": {
            "description": "2 metre temperature",
            "units_raw": str(ds["t2m"].attrs.get("units", "unknown")),
            "units_converted": "degrees Celsius (after -273.15)",
            "standard_name": ds["t2m"].attrs.get("standard_name", "unknown"),
            "long_name": ds["t2m"].attrs.get("long_name", "unknown"),
            "range_raw": [float(ds["t2m"].min()), float(ds["t2m"].max())],
            "range_celsius": [
                float(ds["t2m"].min()) - 273.15,
                float(ds["t2m"].max()) - 273.15,
            ],
            "missing_values": int(ds["t2m"].isnull().sum()),
            "total_values": int(ds["t2m"].size),
        },
        "d2m": {
            "description": "2 metre dewpoint temperature",
            "units_raw": str(ds["d2m"].attrs.get("units", "unknown")),
            "units_converted": "degrees Celsius (after -273.15)",
            "standard_name": ds["d2m"].attrs.get("standard_name", "unknown"),
            "long_name": ds["d2m"].attrs.get("long_name", "unknown"),
            "range_raw": [float(ds["d2m"].min()), float(ds["d2m"].max())],
            "range_celsius": [
                float(ds["d2m"].min()) - 273.15,
                float(ds["d2m"].max()) - 273.15,
            ],
            "missing_values": int(ds["d2m"].isnull().sum()),
            "total_values": int(ds["d2m"].size),
        },
        "u10": {
            "description": "10 metre U wind component",
            "units_raw": str(ds["u10"].attrs.get("units", "unknown")),
            "standard_name": ds["u10"].attrs.get("standard_name", "unknown"),
            "long_name": ds["u10"].attrs.get("long_name", "unknown"),
            "range_raw": [float(ds["u10"].min()), float(ds["u10"].max())],
            "missing_values": int(ds["u10"].isnull().sum()),
            "total_values": int(ds["u10"].size),
        },
        "v10": {
            "description": "10 metre V wind component",
            "units_raw": str(ds["v10"].attrs.get("units", "unknown")),
            "standard_name": ds["v10"].attrs.get("standard_name", "unknown"),
            "long_name": ds["v10"].attrs.get("long_name", "unknown"),
            "range_raw": [float(ds["v10"].min()), float(ds["v10"].max())],
            "missing_values": int(ds["v10"].isnull().sum()),
            "total_values": int(ds["v10"].size),
        },
        "sp": {
            "description": "Surface pressure",
            "units_raw": str(ds["sp"].attrs.get("units", "unknown")),
            "standard_name": ds["sp"].attrs.get("standard_name", "unknown"),
            "long_name": ds["sp"].attrs.get("long_name", "unknown"),
            "range_raw": [float(ds["sp"].min()), float(ds["sp"].max())],
            "missing_values": int(ds["sp"].isnull().sum()),
            "total_values": int(ds["sp"].size),
        },
        "ssrd": {
            "description": "Surface short-wave (solar) radiation downwards",
            "units_raw": str(ds["ssrd"].attrs.get("units", "unknown")),
            "standard_name": ds["ssrd"].attrs.get("standard_name", "unknown"),
            "long_name": ds["ssrd"].attrs.get("long_name", "unknown"),
            "range_raw": [float(ds["ssrd"].min()), float(ds["ssrd"].max())],
            "missing_values": int(ds["ssrd"].isnull().sum()),
            "total_values": int(ds["ssrd"].size),
        },
        "strd": {
            "description": "Surface long-wave (thermal) radiation downwards",
            "units_raw": str(ds["strd"].attrs.get("units", "unknown")),
            "standard_name": ds["strd"].attrs.get("standard_name", "unknown"),
            "long_name": ds["strd"].attrs.get("long_name", "unknown"),
            "range_raw": [float(ds["strd"].min()), float(ds["strd"].max())],
            "missing_values": int(ds["strd"].isnull().sum()),
            "total_values": int(ds["strd"].size),
        },
    }

    # Time analysis
    times = ds.valid_time.values
    time_min = str(times.min())
    time_max = str(times.max())
    timestamp_count = len(times)

    # Check for duplicate timestamps
    unique_timestamps = len(set(str(t) for t in times))
    duplicate_timestamps = timestamp_count - unique_timestamps

    # Spatial analysis
    lats = ds.latitude.values
    lons = ds.longitude.values
    lat_res = abs(float(lats[1] - lats[0])) if len(lats) > 1 else None
    lon_res = abs(float(lons[1] - lons[0])) if len(lons) > 1 else None

    # Grid cell count
    spatial_cell_count = len(lats) * len(lons)

    # Check for missing values across all variables
    total_missing = sum(var_docs[v]["missing_values"] for v in var_docs)

    profile = {
        "dataset_id": "era5land_ahmedabad_2010_03",
        "domain": "weather",
        "source_name": "ERA5-Land",
        "source_type": "PRIMARY_OFFICIAL",
        "source_url": "https://cds.climate.copernicus.eu/",
        "source_file": NC_PATH,
        "source_sha256": sha256_file(NC_PATH),
        "acquired_at": datetime.now(UTC).isoformat(),
        "original_format": "NetCDF (CF-1.6)",
        "transformation_version": "v2.0.0",
        "status": "READY",
        "evidence_classification": "PRIMARY_OFFICIAL",
        "source_status": "VERIFIED",
        "access_status": "PUBLIC",
        "ml_suitability": "PARTIALLY_SUITABLE",
        "notes": "March 2010 sample only. Not full year.",
        "file_size_bytes": Path(NC_PATH).stat().st_size,
        "dimensions": dict(ds.sizes),
        "coordinate_dimensions": list(ds.dims.keys()),
        "variables_present": list(ds.data_vars),
        "required_variables": {
            "t2m": "present" if "t2m" in ds.data_vars else "MISSING",
            "d2m": "present" if "d2m" in ds.data_vars else "MISSING",
            "u10": "present" if "u10" in ds.data_vars else "MISSING",
            "v10": "present" if "v10" in ds.data_vars else "MISSING",
            "sp": "present" if "sp" in ds.data_vars else "MISSING",
            "ssrd": "present" if "ssrd" in ds.data_vars else "MISSING",
            "strd": "present" if "strd" in ds.data_vars else "MISSING",
        },
        "variable_details": var_docs,
        "time_analysis": {
            "time_min": time_min,
            "time_max": time_max,
            "timestamp_count": timestamp_count,
            "unique_timestamps": unique_timestamps,
            "duplicate_timestamps": duplicate_timestamps,
            "time_encoding": str(ds["valid_time"].attrs.get("units", "unknown")),
            "timezone_semantics": "UTC (ERA5 standard)",
        },
        "spatial_analysis": {
            "latitude_range": [float(lats.min()), float(lats.max())],
            "longitude_range": [float(lons.min()), float(lons.max())],
            "latitude_resolution_deg": lat_res,
            "longitude_resolution_deg": lon_res,
            "spatial_cell_count": spatial_cell_count,
            "geographic_extent": "Ahmedabad region (approx 22.8-23.2N, 72.4-72.8E)",
        },
        "quality_checks": {
            "total_missing_values": total_missing,
            "duplicate_timestamps": duplicate_timestamps,
            "all_required_variables_present": all(
                v in ds.data_vars for v in ["t2m", "d2m", "u10", "v10", "sp", "ssrd", "strd"]
            ),
        },
    }

    ds.close()
    return profile


def write_markdown(profile: dict) -> None:
    md_lines = [
        "# ERA5-Land Ahmedabad — Enhanced Profile",
        "",
        f"**Status**: {profile['status']}",
        f"**Source**: {profile['source_name']}",
        f"**Format**: {profile['original_format']}",
        f"**SHA256**: `{profile['source_sha256']}`",
        f"**File size**: {profile['file_size_bytes']:,} bytes",
        "",
        "## Dimensions",
        "",
        "| Dimension | Size |",
        "|-----------|------|",
    ]
    for dim, size in profile["dimensions"].items():
        md_lines.append(f"| {dim} | {size} |")

    md_lines += [
        "",
        "## Required Variables",
        "",
        "| Variable | Status | Description | Units | Range | Missing |",
        "|----------|--------|-------------|-------|-------|---------|",
    ]
    for var_name, status in profile["required_variables"].items():
        details = profile["variable_details"].get(var_name, {})
        range_str = ""
        if "range_celsius" in details:
            range_str = f"{details['range_celsius'][0]:.1f} to {details['range_celsius'][1]:.1f} C"
        elif "range_raw" in details:
            range_str = f"{details['range_raw'][0]:.2f} to {details['range_raw'][1]:.2f}"
        md_lines.append(
            f"| {var_name} | {status} | {details.get('long_name', 'N/A')} | "
            f"{details.get('units_raw', 'N/A')} | {range_str} | "
            f"{details.get('missing_values', 'N/A')} |"
        )

    md_lines += [
        "",
        "## Time Analysis",
        "",
        f"- **Min**: {profile['time_analysis']['time_min']}",
        f"- **Max**: {profile['time_analysis']['time_max']}",
        f"- **Timestamp count**: {profile['time_analysis']['timestamp_count']}",
        f"- **Duplicate timestamps**: {profile['time_analysis']['duplicate_timestamps']}",
        f"- **Timezone**: {profile['time_analysis']['timezone_semantics']}",
        "",
        "## Spatial Analysis",
        "",
        f"- **Latitude range**: {profile['spatial_analysis']['latitude_range']}",
        f"- **Longitude range**: {profile['spatial_analysis']['longitude_range']}",
        f"- **Resolution**: {profile['spatial_analysis']['latitude_resolution_deg']:.2f} deg",
        f"- **Grid cells**: {profile['spatial_analysis']['spatial_cell_count']}",
        "",
        "## Quality Checks",
        "",
        f"- Total missing values: "
        f"{profile['quality_checks']['total_missing_values']}",
        f"- Duplicate timestamps: "
        f"{profile['quality_checks']['duplicate_timestamps']}",
        f"- All required variables present: "
        f"{profile['quality_checks']['all_required_variables_present']}",
        "",
    ]

    Path(OUTPUT_MD).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(md_lines))
    print(f"Markdown written to {OUTPUT_MD}")


def main():
    print("Profiling ERA5-Land...")
    profile = profile_era5()

    Path(OUTPUT_JSON).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(profile, f, indent=2, default=str)
    print(f"JSON written to {OUTPUT_JSON}")

    write_markdown(profile)
    print("Done.")


if __name__ == "__main__":
    main()
