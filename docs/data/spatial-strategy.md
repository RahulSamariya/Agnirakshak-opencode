# Spatial Strategy

**Version**: 1.0
**Status**: ACTIVE

## Geographic Hierarchy

```
India
  └─ Gujarat (State Code: 24)
       └─ Ahmedabad (District Code: 474)
            └─ AMC Wards (48 current / 57 Census 2011)
```

## Data Layers

| Layer | Source | Resolution | CRS |
|-------|--------|-----------|-----|
| Weather (ERA5-Land) | Grid cells | ~9km (0.1°) | WGS84 |
| Ward Boundaries | GIS polygons | Ward-level | WGS84 |
| Census 2011 | Ward-level aggregates | Ward-level | N/A |
| AQI | City-level point | Point (single station) | N/A |

## Spatial Relationships

### ERA5-Land → Wards
- ERA5 grid cells (~9km) intersect multiple wards
- Each ward may receive 0–N cells
- **No interpolation** at profiling stage
- Compatibility measured via point-in-polygon analysis

### Census → Wards
- Census 2011 has 57 AMC wards (2011 delimitation)
- Current GIS has 48 wards (2024 delimitation)
- **Crosswalk required** before joining
- DO NOT direct join

### AQI → Wards
- AQI is city-level (single Ahmedabad reading)
- No ward-level spatial assignment
- Applied uniformly to all wards

## Known Spatial Gaps

1. **Ward crosswalk missing**: Cannot join Census 2011 to current GIS
2. **ERA5 coarse resolution**: 9km cells may not capture intra-urban variability
3. **Single AQI station**: No spatial variability in air quality
