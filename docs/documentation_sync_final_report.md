# Documentation Synchronization Final Report

**Status:** COMPLETE
**Generated:** 2026-09-12T02:05:34.131033
**Method:** Git history as source of truth

---

## LATEST GIT COMMIT

**8dcb853** - docs: synchronize PM2.5 data and model documentation

---

## CURRENT PM2.5 DATA STATE

| Metric | Value | Source |
|--------|-------|--------|
| Total rows | 3285 | `ahmedabad_pm25_station_day_2025.parquet` |
| Eligible rows | 2780 | Same file, daily_qc_flag=ELIGIBLE |
| Stations | 9 | Same file |
| Canonical version | 2780 | Commit 179a074 |
| Historical version | 2737 | Old driver CSV |

---

## CURRENT MAIAC DATA STATE

| Metric | Value | Source |
|--------|-------|--------|
| Total rows | 2737 | `ahmedabad_pm25_maiac_station_day_2025.parquet` |
| Strict AOD available | 596 | Same file |
| AOD coverage | 21.8% | Calculated |
| Extraction completed | Commit f33f3a8 | Git |

---

## CURRENT ERA5 STATE

| Metric | Value | Source |
|--------|-------|--------|
| Total rows | 1728 | `ahmedabad_pm25_era5_pilot_500.csv` |
| Pilot-complete | 500/500 | Same file |
| Extraction completed | Commit 96962e2 | Git |

---

## CURRENT MODEL STATE

| Metric | Value | Source |
|--------|-------|--------|
| Pilot rows | 500 | `ahmedabad_pm25_station_day_2025_pilot_500.parquet` |
| Best model | Random Forest | `pm25_pilot_500_results.csv` |
| Best MAE | 12.17 | Same file |
| Best R2 | 0.500 | Same file |
| Baseline frozen | Commit 179a074 | Git |
| Status | EXPERIMENTAL | Not production-ready |

---

## HISTORICAL STAGES IDENTIFIED

| Stage | Commits | Status |
|-------|---------|--------|
| 1. PM2.5 Target Construction | 6be4027 to 12cc2a1 | COMPLETED |
| 2. MAIAC Acquisition/Validation | 6358f0c to 17ed6d1 | COMPLETED |
| 3. Batch Extraction Architecture | b54bbea to 3674808 | COMPLETED |
| 4. Full 2025 MAIAC Dataset | f33f3a8 | COMPLETED |
| 5. ERA5 Pilot + 500-Row Model | 96962e2 | COMPLETED |
| 6. Baseline Freeze | 179a074 | COMPLETED |
| 7. Documentation Sync | 8dcb853 | COMPLETED |

---

## SUPERSEDED DOCUMENTS

| Document | Reason | Superseded By |
|----------|--------|---------------|
| ahmedabad_pm25_modeling_readiness.md | Earlier pipeline state | ahmedabad_pm25_2025_canonical.md |
| ahmedabad_pm25_matched_dataset_2025.md | Earlier pipeline state | ahmedabad_pm25_2025_canonical.md |
| ahmedabad_pm25_predictor_matching_2025.md | Earlier pipeline state | ahmedabad_pm25_2025_canonical.md |
| ahmedabad_pm25_station_day_2025.md | Earlier pipeline state | ahmedabad_pm25_2025_canonical.md |
| ahmedabad_pm25_2025_modeling_dataset.md | Earlier pipeline state | ahmedabad_pm25_2025_canonical.md |

---

## CANONICAL CURRENT DOCUMENTS

| Document | Path | Purpose |
|----------|------|---------|
| PM2.5 Data | `docs/data/ahmedabad_pm25_2025_canonical.md` | Source of truth for PM2.5 data |
| Model Baseline | `docs/models/pm25_pilot_2025_baseline.md` | Source of truth for pilot model |
| MAIAC Method | `docs/data/maiac_2025_extraction.md` | Source of truth for MAIAC |
| Pipeline | `docs/data/pm25_pipeline_canonical.md` | Conceptual pipeline flow |
| Evolution | `docs/project_evolution.md` | Git-based project history |

---

## UNRESOLVED CONTRADICTIONS

**None.** All contradictions identified and resolved.

---

## GIT COMMITS SUPPORTING MAJOR TRANSITIONS

| Transition | Commit | Description |
|------------|--------|-------------|
| PM2.5 target created | 6be4027 | Build 2025 station-day dataset |
| MAIAC scripts created | 6358f0c | Create extraction scripts |
| Memory bug fixed | 3674808 | Remove getInfo() bug |
| Full MAIAC completed | f33f3a8 | Complete 2025 extraction |
| Pilot model trained | 96962e2 | 500-row pilot with LOSO |
| Baseline frozen | 179a074 | Freeze results |
| Documentation synced | 8dcb853 | Current state |

---

## DOCUMENTATION STATUS

**SYNCHRONIZED**

All documentation now reflects the actual repository state,
verified through Git history analysis.

---

**Status:** COMPLETE - Documentation synchronization finished.
