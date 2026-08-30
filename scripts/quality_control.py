"""Quality control for Ahmedabad pilot data.

Validates ingested data against canonical staging schemas.
Reports missing values, out-of-range, type errors, and duplicates.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime

import xarray as xr
import geopandas as gpd
import pandas as pd


class QCReport:
    """Accumulates quality control findings."""

    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.checks: list[dict] = []
        self.passed = 0
        self.failed = 0

    def add_check(self, name: str, status: str, details: str = ""):
        self.checks.append({
            "check": name,
            "status": status,
            "details": details,
        })
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1

    def summary(self) -> dict:
        return {
            "dataset": self.dataset_name,
            "total_checks": self.passed + self.failed,
            "passed": self.passed,
            "failed": self.failed,
            "overall": "PASS" if self.failed == 0 else "FAIL",
            "checks": self.checks,
        }


def qc_era5land(nc_path: str) -> QCReport:
    """QC for ERA5-Land NetCDF file."""
    report = QCReport("era5land")

    try:
        ds = xr.open_dataset(nc_path)
    except Exception as e:
        report.add_check("file_loads", "FAIL", str(e))
        return report

    report.add_check("file_loads", "PASS")

    # Required variables
    required_vars = ["t2m", "d2m", "u10", "v10", "sp", "ssrd", "strd"]
    for var in required_vars:
        if var in ds.data_vars:
            report.add_check(f"var_{var}_present", "PASS")
        else:
            report.add_check(f"var_{var}_present", "FAIL", "missing")

    # Missing values
    for var in ds.data_vars:
        missing = int(ds[var].isnull().sum().item())
        if missing == 0:
            report.add_check(f"{var}_no_missing", "PASS")
        else:
            report.add_check(
                f"{var}_no_missing", "FAIL",
                f"{missing} missing values"
            )

    # Temperature range (-90 to 60 C)
    if "t2m" in ds.data_vars:
        t_min = float(ds["t2m"].min().item()) - 273.15
        t_max = float(ds["t2m"].max().item()) - 273.15
        if -90 <= t_min <= 60 and -90 <= t_max <= 60:
            report.add_check("t2m_range", "PASS", f"{t_min:.1f} to {t_max:.1f} C")
        else:
            report.add_check("t2m_range", "FAIL", f"{t_min:.1f} to {t_max:.1f} C")

    # Wind speed range (0 to 100 m/s)
    for var in ["u10", "v10"]:
        if var in ds.data_vars:
            # ERA5 stores as m/s, check raw values
            raw_min = float(ds[var].min().item())
            raw_max = float(ds[var].max().item())
            if -100 <= raw_min <= 100 and -100 <= raw_max <= 100:
                report.add_check(f"{var}_range", "PASS", f"{raw_min:.2f} to {raw_max:.2f}")
            else:
                report.add_check(f"{var}_range", "FAIL", f"{raw_min:.2f} to {raw_max:.2f}")

    # Dimension check
    dims = dict(ds.dims)
    if "valid_time" in dims or "time" in dims:
        report.add_check("has_time_dim", "PASS")
    else:
        report.add_check("has_time_dim", "FAIL", f"dims: {list(dims.keys())}")

    if "latitude" in dims and "longitude" in dims:
        report.add_check("has_lat_lon", "PASS")
    else:
        report.add_check("has_lat_lon", "FAIL", f"dims: {list(dims.keys())}")

    ds.close()
    return report


def qc_gis(geojson_path: str) -> QCReport:
    """QC for GIS GeoJSON file."""
    report = QCReport("gis_ahmedabad")

    try:
        gdf = gpd.read_file(geojson_path)
    except Exception as e:
        report.add_check("file_loads", "FAIL", str(e))
        return report

    report.add_check("file_loads", "PASS")

    # Feature count
    report.add_check("feature_count", "PASS", f"{len(gdf)} features")

    # CRS check
    if gdf.crs is not None and gdf.crs.to_epsg() == 4326:
        report.add_check("crs_epsg4326", "PASS")
    else:
        report.add_check("crs_epsg4326", "FAIL", f"CRS: {gdf.crs}")

    # Valid geometries
    invalid = int((~gdf.geometry.is_valid).sum())
    if invalid == 0:
        report.add_check("valid_geometries", "PASS")
    else:
        report.add_check("valid_geometries", "FAIL", f"{invalid} invalid")

    # Empty geometries
    empty = int(gdf.geometry.is_empty.sum())
    if empty == 0:
        report.add_check("no_empty_geometries", "PASS")
    else:
        report.add_check("no_empty_geometries", "FAIL", f"{empty} empty")

    # No duplicate IDs
    if "ward_lgd_code" in gdf.columns:
        dups = int(gdf["ward_lgd_code"].duplicated().sum())
        if dups == 0:
            report.add_check("no_duplicate_ids", "PASS")
        else:
            report.add_check("no_duplicate_ids", "FAIL", f"{dups} duplicates")

    # Required columns
    required_cols = ["ward_lgd_code", "ward_lgd_name"]
    for col in required_cols:
        if col in gdf.columns:
            report.add_check(f"has_{col}", "PASS")
        else:
            report.add_check(f"has_{col}", "FAIL", "missing")

    return report


def qc_aqi(xlsx_dir: str) -> QCReport:
    """QC for AQI Excel files."""
    report = QCReport("aqi_ahmedabad")

    xlsx_files = list(Path(xlsx_dir).glob("*.xlsx"))
    if not xlsx_files:
        report.add_check("files_exist", "FAIL", "no .xlsx files found")
        return report

    report.add_check("files_exist", "PASS", f"{len(xlsx_files)} files")

    total_rows = 0
    total_missing = 0

    for f in sorted(xlsx_files):
        try:
            df = pd.read_excel(f)
            total_rows += len(df)
            report.add_check(f"load_{f.stem[:20]}", "PASS")
        except Exception as e:
            report.add_check(f"load_{f.stem[:20]}", "FAIL", str(e))
            continue

        # Check Date column exists
        if "Date" in df.columns:
            report.add_check(f"date_col_{f.stem[:20]}", "PASS")
        else:
            report.add_check(f"date_col_{f.stem[:20]}", "FAIL", "no Date column")

        # Count missing values across hourly columns
        hourly_cols = [c for c in df.columns if c != "Date"]
        missing = int(df[hourly_cols].isnull().sum().sum())
        total_missing += missing

    report.add_check(
        "total_rows", "PASS", f"{total_rows} rows across {len(xlsx_files)} files"
    )

    missing_pct = (total_missing / (total_rows * 24) * 100) if total_rows > 0 else 0
    if missing_pct < 10:
        report.add_check(
            "missing_values", "PASS",
            f"{missing_pct:.1f}% missing ({total_missing} cells)"
        )
    else:
        report.add_check(
            "missing_values", "FAIL",
            f"{missing_pct:.1f}% missing ({total_missing} cells)"
        )

    return report


def main():
    """Run all QC checks and save report."""
    results = {}

    # ERA5-Land
    nc_path = "data/raw/weather/data_0.nc"
    if Path(nc_path).exists():
        print("Running ERA5-Land QC...")
        results["era5land"] = qc_era5land(nc_path).summary()
    else:
        print(f"SKIP: {nc_path} not found")

    # GIS
    geojson_path = "data/raw/gis/wards_ahmedabad.geojson"
    if Path(geojson_path).exists():
        print("Running GIS QC...")
        results["gis"] = qc_gis(geojson_path).summary()
    else:
        print(f"SKIP: {geojson_path} not found")

    # AQI
    aqi_dir = "data/raw/aqi"
    if Path(aqi_dir).exists():
        print("Running AQI QC...")
        results["aqi"] = qc_aqi(aqi_dir).summary()
    else:
        print(f"SKIP: {aqi_dir} not found")

    # Save report
    output_path = Path("data/profiles/qc_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n=== QC Summary ===")
    for dataset, summary in results.items():
        status = summary["overall"]
        passed = summary["passed"]
        failed = summary["failed"]
        print(f"  {dataset}: {status} ({passed} passed, {failed} failed)")

    all_pass = all(r["overall"] == "PASS" for r in results.values())
    print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
