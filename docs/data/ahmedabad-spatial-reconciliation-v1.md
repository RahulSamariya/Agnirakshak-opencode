# Ahmedabad Spatial Reconciliation

## Census 2011 vs Current GIS

### Census 2011 (AMC Wards)
- **Ward count**: 57
- **Time period**: 2011
- **Source**: Census of India 2011
- **Status**: Historical reference

### Current GIS (2024)
- **Ward count**: 48
- **Time period**: 2024
- **Source**: Ahmedabad Municipal Corporation
- **Status**: Current administrative boundaries

## Comparison

| Aspect | Census 2011 | Current GIS |
|--------|-------------|-------------|
| Ward count | 57 | 48 |
| Difference | +9 wards | -9 wards |
| ID format | `sourcewardcode` | `ward_lgd_code` |
| Geometry | Not provided | Polygon (EPSG:4326) |

## Analysis

### Ward Count Difference
The Census 2011 data references 57 AMC wards, while the current GIS has 48 wards. This indicates:
- Ward delimitation changes between 2011 and 2024
- Some wards may have been merged or split
- Administrative reorganization occurred

### ID Compatibility
- Census IDs: `sourcewardcode` (string format)
- GIS IDs: `ward_lgd_code` (numeric format)
- **No direct ID match** possible without crosswalk

## Status: CROSSWALK_REQUIRED

### Required Actions
1. Obtain 2011 ward boundary shapefile for direct comparison
2. Create ward-level crosswalk mapping 57 → 48 wards
3. Validate crosswalk with Ahmedabad Municipal Corporation

### Do NOT
- Invent crosswalk mappings
- Assume 1:1 ward correspondence
- Merge mismatched 2011/current wards without validation

## Recommendation

**BLOCKED** - Cannot join Census 2011 demographic data to current GIS without:
1. Historical ward boundaries (2011 shapefile)
2. Official crosswalk from AMC
3. Validation of ward mergers/splits
