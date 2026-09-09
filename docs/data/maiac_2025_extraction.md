# MAIAC 2025 Extraction — Improved Selection Strategy

**Generated**: 2026-09-09  
**Status**: Validated — 10-row audit complete  
**Project**: Agnirakshak (Agniraksha)

## Overview

This document describes the improved MAIAC AOD extraction strategy for the 2025 Ahmedabad PM2.5 modeling dataset, including:

- Explicit glint mask check (bit 12 = 0)
- Three separate QA tiers (STRICT_BEST_QUALITY, RESEARCH_QUALITY, DIAGNOSTIC)
- Uncertainty-based overlap selection (lowest uncertainty preferred)
- Station-level extraction with diagnostic neighborhood statistics

## MAIAC Source

**Dataset**: `MODIS/061/MCD19A2_GRANULES`

**Bands**:
- `Optical_Depth_055`: AOD at 550nm (scale: 0.001)
- `AOD_Uncertainty`: AOD uncertainty (scale: 0.0001)
- `AOD_QA`: Quality assurance bits (16-bit unsigned integer)

## Official MCD19A2.061 QA Bit Definition

```
Bits 0-2: Cloud Mask
  000 = Undefined
  001 = Clear
  010 = Possibly Cloudy (detected by AOD filter)
  011 = Cloudy (detected by cloud mask algorithm)
  101 = Cloud Shadow
  110 = Hot spot of fire
  111 = Water Sediments

Bits 3-4: Land Water Snow/Ice Mask
  00 = Land
  01 = Water
  10 = Snow
  11 = Ice

Bits 5-7: Adjacency Mask
  000 = Normal condition/Clear
  001 = Adjacent to clouds
  010 = Surrounded by >4 cloudy pixels
  011 = Adjacent to a single cloudy pixel
  100 = Adjacent to snow
  101 = Snow was previously detected

Bits 8-11: QA for AOD
  0000 = Best quality
  0001 = Water Sediments detected
  0011 = 1 neighbor cloud
  0100 = >1 neighbor clouds
  0101 = No retrieval (cloudy)
  0110 = No retrieval near snow
  0111 = Climatology AOD (high altitude)
  1000 = No retrieval due to sun glint
  1001 = Very low AOD due to glint
  1010 = Coastline replacement
  1011 = Research quality (CM possibly cloudy)

Bit 12: Glint Mask
  0 = No glint
  1 = Glint (glint angle < 40°)

Bits 13-14: Aerosol Model
  00 = Background (regional)
  01 = Smoke (regional)
  10 = Dust
```

## QA Tiers

### TIER 1 — STRICT_BEST_QUALITY

**Requirements**:
- `cloud_mask == 1` (Clear)
- `land_mask == 0` (Land)
- `aod_quality == 0` (Best quality)
- `glint_mask == 0` (No glint)

**Use case**: Production AOD predictor for PM2.5 modeling

### TIER 2 — RESEARCH_QUALITY

**Requirements**:
- `land_mask == 0` (Land)
- `aod_quality == 11` (Research quality: AOD retrieved but CM is possibly cloudy)
- `glint_mask == 0` (No glint)

**Note**: Do not require `cloud_mask == 1` for QA=11 because the official definition specifically permits possibly cloudy pixels for this research-quality category.

**Use case**: Candidate research-quality predictor (if substantial additional coverage)

### TIER 3 — DIAGNOSTIC ONLY

**Requirements**:
- `aod_quality in {3, 4}` (1 neighbor cloud, >1 neighbor clouds)

**Note**: Do NOT make QA 3/4 a production tier. Retain as diagnostic only.

**Use case**: Diagnostic analysis of cloud-adjacent cases

## Glint Filter

**Explicit condition**: `glint_mask == 0` (bit 12 = 0)

This must be explicitly visible in the code. Do not rely on indirect exclusion.

- `bit 12 = 0` → no glint
- `bit 12 = 1` → glint (glint angle < 40°)

## AOD Scaling

For valid `Optical_Depth_055`:
```
aod_550 = Optical_Depth_055 * 0.001
```

For `AOD_Uncertainty`:
```
aod_uncertainty = AOD_Uncertainty * 0.0001
```

Never use raw integer values as physical AOD.

## Overlapping Granule Selection

When multiple valid MAIAC observations/granules overlap the same station/date:

1. Filter by date
2. Filter by station geometry
3. Apply the selected QA tier
4. Remove glint
5. Retain valid AOD and uncertainty
6. Select the observation with the **LOWEST** valid AOD uncertainty

**Important**: AOD_Uncertainty is minimized, not maximized. Therefore do NOT use:
- `qualityMosaic('AOD_Uncertainty')` directly
- Highest uncertainty selection

If using `qualityMosaic`, transform uncertainty into an explicitly documented inverse-quality band, or implement an equivalent minimum-uncertainty selection.

The final code must make it obvious that: **lower uncertainty = preferred observation**.

Do not overwrite AOD with a neighborhood mean.

## Station-Level Output

For each station/date return separately:

| Field | Description |
|-------|-------------|
| `strict_aod_550` | TIER 1 AOD at 550nm |
| `strict_aod_uncertainty` | TIER 1 AOD uncertainty |
| `strict_aod_available` | Boolean: TIER 1 AOD available |
| `research_aod_550` | TIER 2 AOD at 550nm |
| `research_aod_uncertainty` | TIER 2 AOD uncertainty |
| `research_aod_available` | Boolean: TIER 2 AOD available |

Also return diagnostics:

| Field | Description |
|-------|-------------|
| `covering_granules` | Number of MAIAC granules for this date |
| `strict_valid_candidates` | Number of TIER 1 valid candidates |
| `research_valid_candidates` | Number of TIER 2 valid candidates |
| `selected_strict_granule_index` | Index of selected TIER 1 granule |
| `selected_research_granule_index` | Index of selected TIER 2 granule |

Do not claim a value is available when no valid candidate exists.

## Diagnostic Neighborhood

Neighborhood calculations may be retained only as diagnostics.

For each tier optionally calculate:
- `valid_neighbor_pixel_count`
- `neighborhood_mean_aod`

But these MUST NOT replace a missing station-pixel value.

Do not use neighborhood mean as the primary AOD predictor.

## Validation Results

### 10-Row Audit Dataset

| Metric | Result |
|--------|--------|
| STRICT VALID ROWS | 1/10 |
| RESEARCH VALID ROWS | 0/10 |
| QA3 DIAGNOSTIC ROWS | 0/10 |
| QA4 DIAGNOSTIC ROWS | 0/10 |

### Detailed Results

| Station | Date | Granules | Strict AOD | Strict Unc | Research AOD | Research Unc | QA3 | QA4 |
|---------|------|----------|------------|------------|--------------|--------------|-----|-----|
| Gyaspur | 2025-01-03 | 1293 | None | None | None | None | No | No |
| SVPI Airport Hansol | 2025-02-24 | 1380 | None | None | None | None | No | No |
| Maninagar | 2025-03-29 | 1470 | 0.236 | 0.0174 | None | None | No | No |
| Chandkheda | 2025-04-10 | 1467 | None | None | None | None | No | No |
| Chandkheda | 2025-05-26 | 1441 | None | None | None | None | No | No |
| SAC ISRO Satellite | 2025-06-14 | 1494 | None | None | None | None | No | No |
| SAC ISRO Bopal | 2025-07-25 | 1462 | None | None | None | None | No | No |
| Maninagar | 2025-08-29 | 1441 | None | None | None | None | No | No |
| SAC ISRO Bopal | 2025-09-25 | 1411 | None | None | None | None | No | No |
| Chandkheda | 2025-10-10 | 1335 | None | None | None | None | No | No |

### Verification

| Check | Status |
|-------|--------|
| LOWEST-UNCERTAINTY SELECTION VERIFIED | N/A (no overlap cases) |
| GLINT MASK VERIFIED | PASS |
| QA TIER SEPARATION VERIFIED | PASS |

## Scientific Integrity

**Never**:
- Use unmasked AOD
- Use QA=5 no-retrieval
- Use glint-contaminated observations
- Impute missing AOD
- Substitute neighborhood means
- Silently mix strict and research tiers
- Choose highest uncertainty
- Use `first()` to resolve spatial overlap

## Files

| File | Description |
|------|-------------|
| `scripts/earth_engine/validate_maiac_selection_2025.py` | Validation script |
| `scripts/earth_engine/extract_ahmedabad_pm25_maiac_2025.py` | Main extraction script |
| `data/metadata/maiac_2025_selection_validation.csv` | Validation results |

## Next Steps

1. Run full 2737 station-day extraction with improved logic
2. Assess coverage under each QA tier
3. Determine production QA rule based on coverage evidence
4. Proceed to baseline model training