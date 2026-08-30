# GIS Ahmedabad — Enhanced Profile v2

**Status**: READY
**Source**: Ahmedabad Municipal Corporation
**Format**: GeoJSON
**SHA256**: `c5015c0cd147118e34ddf60fccce4f4c93d72118b21ae5d5dc36d1723c17043a`
**File size**: 226,794 bytes

## Feature Summary

| Property | Value |
|----------|-------|
| Feature count | 48 |
| Geometry type | <ArrowStringArray>
['Polygon']
Length: 1, dtype: str |
| CRS | EPSG:4326 |
| Ward ID column | ward_lgd_code |
| Unique ward IDs | 48 |
| Duplicate ward IDs | 0 |
| Invalid geometries | 0 |
| Empty geometries | 0 |

## Coordinate Order Verification

| Check | Result |
|-------|--------|
| Detected order | `latitude_longitude` |
| X range | [22.9121407, 23.1386475] |
| Y range | [72.4472434, 72.7036946] |
| Latitude range | [22.9121407, 23.1386475] |
| Longitude range | [72.4472434, 72.7036946] |

**Ahmedabad geography**: lat ~22.9-23.1, lon ~72.4-72.7

## Normalization

| Property | Value |
|----------|-------|
| Original order | `latitude_longitude` |
| Normalized order | `longitude_latitude` |
| Transformation | swapped lat/lon to lon/lat per GeoJSON spec |
| Original hash | `c5015c0cd147118e34ddf60fccce4f4c93d72118b21ae5d5dc36d1723c17043a` |
| Normalized hash | `e421811c18df3adc2ac8c4cbe9d620df4a963b7df057d4065f1ac9f736e224dc` |

## Columns

- `tessellate`
- `extrude`
- `visibility`
- `objectid`
- `townname`
- `towncensuscode2011`
- `town_lgd_code`
- `ward_lgd_code`
- `ward_lgd_name`
- `sourcewardname`
- `sourcewardcode`
- `state`
- `geometry`

## Known Limitations

- Current GIS has 48 wards (2024 delimitation)
- Census 2011 had 57 wards — **CROSSWALK REQUIRED**
