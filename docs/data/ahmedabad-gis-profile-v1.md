# Ahmedabad Wards GIS Profile

## File
`ERA5/wards_ahmedabad.geojson`

## Feature Count
48 wards

## Properties
| Field | Type | Unique Values | Notes |
|-------|------|---------------|-------|
| `objectid` | float64 | 48 | Unique ward identifier |
| `ward_lgd_code` | float64 | 48 | LGD ward code |
| `ward_lgd_name` | str | 48 | Ward name |
| `sourcewardname` | str | 48 | Source ward name |
| `sourcewardcode` | str | 48 | Source ward code |
| `townname` | str | 1 | All wards in same town |
| `towncensuscode2011` | str | 1 | Census code |
| `town_lgd_code` | float64 | 1 | LGD town code |
| `state` | str | 1 | Gujarat |

## Coordinate Reference System
- **CRS**: EPSG:4326 (WGS84)
- **Axis order**: [latitude, longitude] (GeoJSON standard)

## Bounding Box
- **Min Latitude**: 22.9121°N
- **Min Longitude**: 72.4472°E
- **Max Latitude**: 23.1386°N
- **Max Longitude**: 72.7037°E

## Geometry
- **Type**: Polygon
- **Invalid geometries**: 0
- **Empty geometries**: 0

## Data Quality
- All 48 features have valid geometries
- No duplicate ward IDs
- Source file hash (SHA-256): c5015c0cd147118e34ddf60fccce4f4c93d72118b21ae5d5dc36d1723c17043a

## Notes
- Current GIS has 48 wards (2024 configuration)
- Census 2011 has 57 wards (historical configuration)
- **CROSSWALK REQUIRED** between Census 2011 and current GIS
