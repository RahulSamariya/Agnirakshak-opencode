# Documentation Consistency Report

**Status:** CURRENT
**Generated:** 2026-09-09T19:34:30.191656

---

## Summary

| Check | Status |
|-------|--------|
| Current row count | RESOLVED |
| Historical row count | HISTORICAL |
| Current MAIAC coverage | CURRENT |
| Current ERA5 status | CURRENT |
| Pilot row count | CURRENT |
| Model metrics | CURRENT |
| Station count | CURRENT |
| Coordinate references | CURRENT |
| Status labels | RESOLVED |
| Obsolete next steps | RESOLVED |
| Duplicated sources of truth | RESOLVED |

---

## Detailed Findings

### 1. Current Row Count

**Canonical:** 2780 eligible station-days
**Historical:** 2737 (old driver CSV)
**Difference:** 43 Maninagar station-days
**Status:** RESOLVED

### 2. MAIAC Coverage

**Strict AOD:** 596 / 2737 = 21.8%
**QA=11:** 0
**Status:** CURRENT

### 3. ERA5 Status

**Pilot dataset:** 1728 rows (192 dates x 9 stations)
**ERA5-complete:** 500/500 pilot rows
**Status:** CURRENT

### 4. Pilot Row Count

**Total:** 500 rows
**ERA5-complete:** 500
**AOD-complete:** 92
**Status:** CURRENT

### 5. Model Metrics

| Model | MAE | RMSE | R2 |
|-------|-----|------|----|
| RF (ERA5-only) | 12.17 | 15.75 | 0.500 |
| Ridge (ERA5-only) | 14.56 | 18.72 | 0.335 |
| GBM (ERA5-only) | 12.53 | 16.39 | 0.446 |
**Status:** CURRENT

### 6. Station Count

**Stations:** 9
**Status:** CURRENT

### 7. Coordinate References

**Canonical source:** `data/metadata/ahmedabad_station_coordinate_verification.csv`
**Status:** CURRENT

### 8. Status Labels

**Old documents:** Marked HISTORICAL/SUPERSEDED
**New documents:** Have correct status headers
**Status:** RESOLVED

### 9. Obsolete Next Steps

**Old instructions:** "Retrieve ERA5 data" (already done)
**Current status:** ERA5 extracted and available
**Status:** RESOLVED

### 10. Duplicated Sources of Truth

**Canonical PM2.5 data:** `docs/data/ahmedabad_pm25_2025_canonical.md`
**Canonical model:** `docs/models/pm25_pilot_2025_baseline.md`
**Status:** RESOLVED

---

## Documentation Created

| Document | Status |
|----------|--------|
| `docs/README.md` | CREATED |
| `docs/data/README.md` | CREATED |
| `docs/models/README.md` | CREATED |
| `docs/decisions/README.md` | CREATED |
| `docs/archive/README.md` | CREATED |
| `docs/data/ahmedabad_pm25_2025_canonical.md` | CREATED |
| `docs/models/pm25_pilot_2025_baseline.md` | CREATED |
| `docs/data/maiac_2025_extraction.md` | UPDATED |
| `docs/DOCUMENTATION_GOVERNANCE.md` | CREATED |
| `docs/decisions/001_2025_target_version.md` | CREATED |
| `docs/decisions/002_maiac_strict_qa.md` | CREATED |
| `docs/decisions/003_maiac_batch_export_architecture.md` | CREATED |
| `docs/decisions/004_pm25_500_row_pilot.md` | CREATED |
| `docs/decisions/005_loso_validation_strategy.md` | CREATED |

---

## Documents Marked Historical

| Document | Status |
|----------|--------|
| `ahmedabad_pm25_modeling_readiness.md` | HISTORICAL |
| `ahmedabad_pm25_matched_dataset_2025.md` | HISTORICAL |
| `ahmedabad_pm25_predictor_matching_2025.md` | HISTORICAL |
| `ahmedabad_pm25_station_day_2025.md` | HISTORICAL |
| `ahmedabad_pm25_2025_modeling_dataset.md` | HISTORICAL |

---

## Contradictions Found and Resolved

| Contradiction | Resolution |
|---------------|------------|
| "PM2.5 not available" | Updated: 2780 eligible rows available |
| "MAIAC not retrieved" | Updated: 2737 rows extracted, 596 AOD |
| "ERA5 not retrieved" | Updated: 1728 rows extracted |
| "modeling blocked" | Updated: Pilot models trained |
| "2737" as canonical | Updated: 2780 is canonical |

---

**Status:** CURRENT - All contradictions resolved.
