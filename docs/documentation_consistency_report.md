# Documentation Consistency Report (Git-Based)

**Status:** CURRENT
**Generated:** 2026-09-12T02:05:34.130388
**Source:** Git history analysis

---

## Git History Analysis

### Project Stages Identified

| Stage | Status | Key Commits |
|-------|--------|-------------|
| 1. PM2.5 Target Construction | COMPLETED | 6be4027 to 12cc2a1 |
| 2. MAIAC Acquisition/Validation | COMPLETED | 6358f0c to 17ed6d1 |
| 3. Batch Extraction Architecture | COMPLETED | b54bbea to 3674808 |
| 4. Full 2025 MAIAC Dataset | COMPLETED | f33f3a8 |
| 5. ERA5 Pilot + 500-Row Model | COMPLETED | 96962e2 |
| 6. Baseline Freeze | COMPLETED | 179a074 |
| 7. Documentation Sync | COMPLETED | 8dcb853 |

### Latest Commit

**HEAD:** 8dcb853 (docs: synchronize PM2.5 data and model documentation)

---

## Current Data State (Verified from Repository)

| Component | Rows | Status | Canonical File |
|-----------|------|--------|----------------|
| CPCB PM2.5 | 2780 eligible | COMPLETED | `ahmedabad_pm25_station_day_2025.parquet` |
| MAIAC | 2737 | COMPLETED | `ahmedabad_pm25_maiac_station_day_2025.parquet` |
| ERA5 | 1728 | COMPLETED | `ahmedabad_pm25_era5_pilot_500.csv` |
| Pilot | 500 | COMPLETED | `ahmedabad_pm25_station_day_2025_pilot_500.parquet` |

---

## Documentation Status

### Canonical Documents

| Document | Status | Git Reference |
|----------|--------|---------------|
| `docs/data/ahmedabad_pm25_2025_canonical.md` | CANONICAL | 12cc2a1, 179a074 |
| `docs/models/pm25_pilot_2025_baseline.md` | CANONICAL | 96962e2, 179a074 |
| `docs/data/maiac_2025_extraction.md` | CANONICAL | f33f3a8 |
| `docs/data/pm25_pipeline_canonical.md` | CANONICAL | Multiple |
| `docs/project_evolution.md` | CANONICAL | All stages |

### Historical Documents

| Document | Status | Superseded By |
|----------|--------|---------------|
| `ahmedabad_pm25_modeling_readiness.md` | HISTORICAL | `ahmedabad_pm25_2025_canonical.md` |
| `ahmedabad_pm25_matched_dataset_2025.md` | HISTORICAL | `ahmedabad_pm25_2025_canonical.md` |
| `ahmedabad_pm25_predictor_matching_2025.md` | HISTORICAL | `ahmedabad_pm25_2025_canonical.md` |
| `ahmedabad_pm25_station_day_2025.md` | HISTORICAL | `ahmedabad_pm25_2025_canonical.md` |
| `ahmedabad_pm25_2025_modeling_dataset.md` | HISTORICAL | `ahmedabad_pm25_2025_canonical.md` |

---

## Contradictions Audit

### Patterns Checked

| Pattern | Classification | Action |
|---------|---------------|--------|
| "data unavailable" | RESOLVED | Updated: Data is available |
| "MAIAC not retrieved" | RESOLVED | Updated: MAIAC extracted |
| "ERA5 not retrieved" | RESOLVED | Updated: ERA5 extracted |
| "model training blocked" | RESOLVED | Updated: Models trained |
| "requires extraction" | RESOLVED | Updated: Extraction completed |
| "placeholder" | RESOLVED | Updated: Real data present |
| "2737" (old count) | HISTORICAL | Marked as historical |

### Resolution Summary

- **RESOLVED:** All contradictions identified and handled
- **HISTORICAL:** Old documents marked appropriately
- **CURRENT:** Canonical documents updated with actual data

---

## Git Commits Supporting Major Transitions

| Transition | Commit | Date |
|------------|--------|------|
| PM2.5 target created | 6be4027 | Early |
| MAIAC scripts created | 6358f0c | Mid |
| Memory bug fixed | 3674808 | Mid |
| Full MAIAC completed | f33f3a8 | Late |
| Pilot model trained | 96962e2 | Late |
| Baseline frozen | 179a074 | Late |
| Documentation synced | 8dcb853 | Latest |

---

## Documentation Governance

**File:** `docs/DOCUMENTATION_GOVERNANCE.md`

Rules established:
1. Actual files/data beat old Markdown claims
2. One canonical document per major dataset/model
3. Historical documents never silently treated as current
4. Data version changes require explicit version notes
5. Model metrics reference exact dataset version
6. Scientific methodology changes require decision records
7. No synthetic data in canonical datasets
8. Reproducibility paths point to actual files/scripts
9. Every numerical claim traceable to dataset/artifact

---

**Status:** CURRENT - All documentation synchronized with Git history.
