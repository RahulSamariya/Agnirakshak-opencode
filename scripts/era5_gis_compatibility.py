"""ERA5 grid vs GIS spatial compatibility analysis."""
from __future__ import annotations

import json
from pathlib import Path

import xarray as xr
import geopandas as gpd
import shapely


NC_PATH = "data/raw/weather/data_0.nc"
GEOJSON_PATH = "data/staging/gis/wards_ahmedabad_epsg4326_normalized.geojson"
OUTPUT_MD = "docs/data/ahmedabad-era5-gis-compatibility-v1.md"


def analyze_spatial_compatibility() -> dict:
    ds = xr.open_dataset(NC_PATH)
    lats = ds.latitude.values
    lons = ds.longitude.values
    ds.close()

    gdf = gpd.read_file(GEOJSON_PATH)

    # Build ERA5 grid cells as polygons
    # ERA5 cells are centered on lat/lon points with spacing = resolution
    lat_res = abs(float(lats[1] - lats[0])) if len(lats) > 1 else 0.1
    lon_res = abs(float(lons[1] - lons[0])) if len(lons) > 1 else 0.1

    era5_cells = []
    for lat in lats:
        for lon in lons:
            cell = shapely.geometry.box(
                float(lon) - lon_res / 2,
                float(lat) - lat_res / 2,
                float(lon) + lon_res / 2,
                float(lat) + lat_res / 2,
            )
            era5_cells.append({
                "lat": float(lat),
                "lon": float(lon),
                "geometry": cell,
            })

    era5_gdf = gpd.GeoDataFrame(era5_cells, crs="EPSG:4326")
    total_cells = len(era5_gdf)

    # Point-in-polygon: cell center vs ward polygon
    cells_intersecting_ward = set()
    ward_hit_by_cell = set()
    cells_multi_ward = []

    for idx, cell in era5_gdf.iterrows():
        center = cell.geometry.centroid
        matching_wards = []
        for ward_idx, ward in gdf.iterrows():
            if ward.geometry.contains(center):
                ward_id = str(gdf.iloc[ward_idx].get("ward_lgd_code", ward_idx))
                matching_wards.append(ward_id)
                ward_hit_by_cell.add(ward_id)
                cells_intersecting_ward.add(idx)

        if len(matching_wards) > 1:
            cells_multi_ward.append({
                "cell_idx": idx,
                "lat": cell["lat"],
                "lon": cell["lon"],
                "wards": matching_wards,
            })

    # Polygon intersection: cell polygon vs ward polygon
    cells_intersecting_polygon = set()
    ward_hit_by_polygon = set()

    for idx, cell in era5_gdf.iterrows():
        for ward_idx, ward in gdf.iterrows():
            if cell.geometry.intersects(ward.geometry):
                ward_id = str(gdf.iloc[ward_idx].get("ward_lgd_code", ward_idx))
                ward_hit_by_polygon.add(ward_id)
                cells_intersecting_polygon.add(idx)

    wards_zero_intersections = set(gdf["ward_lgd_code"].astype(str)) - ward_hit_by_polygon

    result = {
        "total_era5_cells": total_cells,
        "cells_intersecting_ahmedabad": len(cells_intersecting_polygon),
        "cells_intersecting_ward_point": len(cells_intersecting_ward),
        "cells_intersecting_ward_polygon": len(cells_intersecting_polygon),
        "wards_hit_point": len(ward_hit_by_cell),
        "wards_hit_polygon": len(ward_hit_by_polygon),
        "wards_with_zero_intersections": sorted(wards_zero_intersections),
        "ward_count_total": len(gdf),
        "cells_intersecting_multiple_wards": len(cells_multi_ward),
        "multi_ward_cells": cells_multi_ward[:10],
        "era5_grid": {
            "lat_range": [float(lats.min()), float(lats.max())],
            "lon_range": [float(lons.min()), float(lons.max())],
            "lat_resolution": lat_res,
            "lon_resolution": lon_res,
        },
    }

    return result


def write_markdown(result: dict) -> None:
    md = f"""# ERA5-GIS Spatial Compatibility Analysis

## ERA5 Grid

| Property | Value |
|----------|-------|
| Latitude range | {result['era5_grid']['lat_range']} |
| Longitude range | {result['era5_grid']['lon_range']} |
| Latitude resolution | {result['era5_grid']['lat_resolution']:.2f} deg |
| Longitude resolution | {result['era5_grid']['lon_resolution']:.2f} deg |
| Total grid cells | {result['total_era5_cells']} |

## GIS Wards

| Property | Value |
|----------|-------|
| Total wards | {result['ward_count_total']} |
| Wards hit (point) | {result['wards_hit_point']} |
| Wards hit (polygon) | {result['wards_hit_polygon']} |
| Wards with zero intersections | {len(result['wards_with_zero_intersections'])} |

## Spatial Intersection Results

| Method | Cells intersecting | Wards hit |
|--------|--------------------|-----------|
| Point-in-polygon | {result['cells_intersecting_ward_point']} | {result['wards_hit_point']} |
| Polygon intersection | {result['cells_intersecting_ward_polygon']} | {result['wards_hit_polygon']} |

## Multi-ward Cells

Cells intersecting multiple wards: {result['cells_intersecting_multiple_wards']}

"""

    if result["wards_with_zero_intersections"]:
        md += "## Wards with Zero ERA5 Intersections\n\n"
        for ward_id in result["wards_with_zero_intersections"]:
            md += f"- Ward {ward_id}\n"
        md += "\n"

    if result["multi_ward_cells"]:
        md += "## Multi-ward Cell Details\n\n"
        md += "| Cell | Lat | Lon | Wards |\n|------|-----|-----|-------|\n"
        for cell in result["multi_ward_cells"]:
            md += f"| {cell['cell_idx']} | {cell['lat']:.2f} | {cell['lon']:.2f} | {', '.join(cell['wards'])} |\n"
        md += "\n"

    md += """## Interpretation

- **Point-in-polygon**: Checks if ERA5 cell center falls within a ward boundary
- **Polygon intersection**: Checks if ERA5 cell polygon overlaps any ward boundary
- Both methods report their results for comparison
- No aggregation rule is chosen at this stage
- This is only a spatial compatibility analysis
"""

    Path(OUTPUT_MD).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MD, "w") as f:
        f.write(md)
    print(f"Markdown written to {OUTPUT_MD}")


def main():
    print("Analyzing ERA5-GIS spatial compatibility...")
    result = analyze_spatial_compatibility()

    # Save JSON
    json_path = "data/profiles/era5_gis_compatibility.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"JSON written to {json_path}")

    write_markdown(result)
    print("Done.")


if __name__ == "__main__":
    main()
