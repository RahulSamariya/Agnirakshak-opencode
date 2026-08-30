# Census 2011 vs Current 48-Ward GIS — Spatial Reconciliation v2

**Status**: CROSSWALK_REQUIRED

## Summary

| Property | Census 2011 | Current GIS |
|----------|-------------|-------------|
| Ward count | 57 | 48 |
| Source | Census of India | Ahmedabad Municipal Corporation |
| Delimitation year | 2011 | 2024 |
| ID format | Census ward code | `ward_lgd_code` |
| Status | Historical | Current |

## Analysis

### Ward Count Difference

The Census 2011 references **57 AMC wards** while the current GIS has **48 wards**. This is a difference of 9 wards, indicating:

- Ward delimitation changed between 2011 and 2024
- Some wards were merged or split
- Administrative reorganization occurred

### ID Compatibility

| Property | Census 2011 | Current GIS |
|----------|-------------|-------------|
| Primary ID | Census ward code | `ward_lgd_code` |
| Secondary ID | Source ward code | `sourcewardcode` |
| LGD code | Not available | `ward_lgd_code` |
| Ward name | Available | `ward_lgd_name` |

- No direct ID match is possible between Census 2011 and current GIS
- The `ward_lgd_code` in GIS is a modern LGD identifier, not present in 2011 Census

### Name Overlap

Cannot verify name overlap without the Census file (BLOCKED).

### Possible Geography Differences

1. **Ward merging**: Some small 2011 wards may have been combined
2. **Ward splitting**: Some large 2011 wards may have been divided
3. **Boundary adjustment**: Ward boundaries may have shifted
4. **Renumbering**: Ward codes may have been reassigned

## Recommendation

**CROSSWALK_REQUIRED** — Cannot join Census 2011 demographic data to current GIS without:

1. Official 2011 ward boundary shapefile (for direct spatial comparison)
2. AMC ward crosswalk document (2011 → 2024 mapping)
3. Validation from Ahmedabad Municipal Corporation

## What NOT to do

- Do NOT invent a crosswalk mapping
- Do NOT assume 1:1 ward correspondence
- Do NOT silently aggregate Census records into current wards
- Do NOT force IDs to match

## Output

Status documented. No data joined.
