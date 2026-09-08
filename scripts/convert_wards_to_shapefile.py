"""Convert verified canonical 48-ward GeoJSON to ESRI Shapefile for Earth Engine."""
import json
import zipfile
import shutil
from pathlib import Path

import geopandas as gpd

SRC = Path("data/staging/gis/wards_ahmedabad_epsg4326_normalized.geojson")
OUT_DIR = Path("data/staging/gis/earth_engine")
OUT_SHP = OUT_DIR / "wards_ahmedabad_48.shp"
OUT_ZIP = OUT_DIR / "wards_ahmedabad_48.zip"
COMPONENTS = [".shp", ".shx", ".dbf", ".prj"]

print("=" * 60)
print("GEOJSON -> SHAPEFILE CONVERSION")
print("=" * 60)

# 1. Read source
print(f"\n[1] Reading source: {SRC}")
gdf = gpd.read_file(SRC)
print(f"    Features: {len(gdf)}")
print(f"    CRS: {gdf.crs}")
print(f"    Columns: {list(gdf.columns)}")
print(f"    Geometry type: {gdf.geometry.geom_type.unique()}")

# 2. Validate source
assert len(gdf) == 48, f"Expected 48 features, got {len(gdf)}"
assert gdf.geometry.is_valid.all(), "Invalid geometries found"
assert not gdf.geometry.is_empty.any(), "Empty geometries found"
assert gdf.geometry.geom_type.unique().tolist() == ["Polygon"], "Non-polygon geometries"
print("    Source validation: PASSED (48 valid polygons)")

# 3. Verify key attributes exist
assert "ward_lgd_code" in gdf.columns, "ward_lgd_code missing"
assert "ward_lgd_name" in gdf.columns, "ward_lgd_name missing"
assert gdf["ward_lgd_code"].nunique() == 48, "Duplicate ward_lgd_code"
assert gdf["ward_lgd_name"].nunique() == 48, "Duplicate ward_lgd_name"
print("    Attributes verified: ward_lgd_code (48 unique), ward_lgd_name (48 unique)")

# 4. Create output directory
OUT_DIR.mkdir(parents=True, exist_ok=True)
print(f"\n[2] Output directory: {OUT_DIR}")

# 5. Write shapefile
print(f"\n[3] Writing shapefile: {OUT_SHP}")
# Shapefile has 10-char field name limit; rename long columns
gdf_out = gdf.copy()
# Manual rename to avoid duplicates
rename_map = {
    "tessellate": "tessellat",
    "towncensuscode2011": "twn_census",
    "town_lgd_code": "tw_lgd_cd",
    "ward_lgd_code": "wrd_lgd_c",
    "ward_lgd_name": "wrd_lgd_n",
    "sourcewardname": "src_wardnm",
    "sourcewardcode": "src_wrdcd",
}
gdf_out = gdf_out.rename(columns=rename_map)
print(f"    Renamed columns for shapefile limit: {rename_map}")

gdf_out.to_file(OUT_SHP, driver="ESRI Shapefile", encoding="utf-8")
print("    Written successfully.")

# 6. Verify output components
print(f"\n[4] Verifying output components:")
for ext in COMPONENTS:
    fpath = OUT_DIR / f"wards_ahmedabad_48{ext}"
    assert fpath.exists(), f"Missing: {fpath}"
    size = fpath.stat().st_size
    print(f"    {fpath.name}: {size:,} bytes")

# 7. Re-read and validate shapefile
print(f"\n[5] Re-reading shapefile for validation:")
gdf_check = gpd.read_file(OUT_SHP)
print(f"    Features: {len(gdf_check)}")
print(f"    CRS: {gdf_check.crs}")
print(f"    Columns: {list(gdf_check.columns)}")
print(f"    Geometry type: {gdf_check.geometry.geom_type.unique()}")
assert len(gdf_check) == 48, f"Output has {len(gdf_check)} features, expected 48"
assert gdf_check.geometry.is_valid.all(), "Invalid geometries in output"
assert not gdf_check.geometry.is_empty.any(), "Empty geometries in output"
print("    Output validation: PASSED (48 valid polygons)")

# 8. Create ZIP
print(f"\n[6] Creating ZIP: {OUT_ZIP}")
with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for ext in COMPONENTS:
        fpath = OUT_DIR / f"wards_ahmedabad_48{ext}"
        zf.write(fpath, fpath.name)
        print(f"    Added: {fpath.name}")
zip_size = OUT_ZIP.stat().st_size
print(f"    ZIP size: {zip_size:,} bytes")

# 9. Verify ZIP contents
print(f"\n[7] ZIP contents:")
with zipfile.ZipFile(OUT_ZIP, "r") as zf:
    for info in zf.infolist():
        print(f"    {info.filename}: {info.file_size:,} bytes")

# 10. Final summary
print("\n" + "=" * 60)
print("FINAL RESULT")
print("=" * 60)
print(f"Source:     {SRC}")
print(f"Shapefile:  {OUT_SHP}")
print(f"ZIP:        {OUT_ZIP}")
print(f"Features:   {len(gdf_check)}")
print(f"CRS:        {gdf_check.crs}")
print(f"Geometry:   {gdf_check.geometry.geom_type.unique().tolist()}")
print(f"Valid:      {gdf_check.geometry.is_valid.all()}")
print(f"Components: {', '.join(f'wards_ahmedabad_48{e}' for e in COMPONENTS)}")
print("=" * 60)
print("CONVERSION COMPLETE")
