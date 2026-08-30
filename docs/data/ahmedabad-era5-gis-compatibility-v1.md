# ERA5-GIS Spatial Compatibility Analysis

## ERA5 Grid

| Property | Value |
|----------|-------|
| Latitude range | [22.8, 23.2] |
| Longitude range | [72.4, 72.8] |
| Latitude resolution | 0.10 deg |
| Longitude resolution | 0.10 deg |
| Total grid cells | 25 |

## GIS Wards

| Property | Value |
|----------|-------|
| Total wards | 48 |

## Spatial Intersection Results

### A. ERA5 Cell Centers / Point-in-Polygon

| Metric | Value |
|--------|-------|
| Grid-cell centers falling inside wards | 4 |
| Wards receiving at least one cell center | 4 |

Method: Tests whether the geographic center of each ERA5 grid cell falls within a ward polygon.

### B. ERA5 Cell Polygons / Area Intersection

| Metric | Value |
|--------|-------|
| Grid cells intersecting wards | 11 |
| Wards intersected | 48 |
| Wards with zero intersections | 0 |

Method: Tests whether the area of each ERA5 grid cell overlaps with any ward polygon.

## Why the Numbers Differ

The ERA5 grid has a coarse resolution (~11 km per cell). Ahmedabad wards are small
polygons (~2-5 km across). As a result:

- **Few cell centers fall inside wards** (4 out of 25) because the grid is coarse
  relative to ward size, and cell centers may land outside ward boundaries.
- **Many cell areas intersect wards** (11 out of 25 cells, covering all 48 wards)
  because each cell covers a large area that spans multiple ward boundaries.

This is not a contradiction — it reflects the difference between testing a single
point (cell center) versus testing an area (cell polygon) against ward boundaries.

## Multi-ward Cells

Cells intersecting multiple wards: 0

## Interpretation

- Both methods report their results for comparison
- No interpolation or ward aggregation method is chosen at this stage
- This is only a spatial compatibility analysis
- The choice of point vs area assignment will be made in the scientific milestone
