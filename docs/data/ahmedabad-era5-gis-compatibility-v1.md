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
| Wards hit (point) | 4 |
| Wards hit (polygon) | 48 |
| Wards with zero intersections | 0 |

## Spatial Intersection Results

| Method | Cells intersecting | Wards hit |
|--------|--------------------|-----------|
| Point-in-polygon | 4 | 4 |
| Polygon intersection | 11 | 48 |

## Multi-ward Cells

Cells intersecting multiple wards: 0

## Interpretation

- **Point-in-polygon**: Checks if ERA5 cell center falls within a ward boundary
- **Polygon intersection**: Checks if ERA5 cell polygon overlaps any ward boundary
- Both methods report their results for comparison
- No aggregation rule is chosen at this stage
- This is only a spatial compatibility analysis
