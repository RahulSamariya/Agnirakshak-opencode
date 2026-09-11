# AGNIRAKSHAK Project Evolution

**Status:** CANONICAL
**Version:** 1.0
**Generated:** 2026-09-12T02:05:34.050661
**Source:** Git commit history

---

## Overview

This document traces the AGNIRAKSHAK project's structural evolution
using Git commits as the authoritative source of truth.

---

## Stage 1: PM2.5 Target Construction

**Status:** COMPLETED
**Commits:** 6be4027 to 12cc2a1

### Key Commits

| Commit | Description |
|--------|-------------|
| 6be4027 | Build 2025 Ahmedabad PM2.5 station-day modeling dataset |
| fb7fbeb | Verify station coordinates and raw PM2.5 file integrity |
| 7fd6999 | Build 2025 Ahmedabad station-day matched dataset |
| faefc28 | Build 2025 Ahmedabad station-day matched dataset with predictor methodology |
| 43b1e6d | Add raw PM2.5 hourly data files for 9 Ahmedabad stations |
| 12cc2a1 | Complete 2025 Ahmedabad PM2.5 modeling data pipeline |

### What Was Built

- Hourly CPCB PM2.5 data ingestion for 9 stations
- Daily station-day aggregation (>= 18 valid hours)
- Station coordinate verification
- Raw file integrity checks
- Canonical PM2.5 target dataset

### Current Canonical Output

**File:** `data/curated/air_quality/ahmedabad_pm25_station_day_2025.parquet`
**Rows:** 2780 eligible station-days
**Stations:** 9

---

## Stage 2: MAIAC Acquisition/Validation

**Status:** COMPLETED
**Commits:** 6358f0c to 17ed6d1

### Key Commits

| Commit | Description |
|--------|-------------|
| 6358f0c | Create Earth Engine extraction scripts for MAIAC AOD + ERA5 |
| c948840 | Correct MAIAC AOD QA masking with official bit definition |
| f951a57 | MAIAC coverage audit - 10 station/date samples |
| c9bc791 | Expanded MAIAC QA coverage audit - 150 station/day samples |
| 17ed6d1 | MAIAC selection validation with QA tiers, glint filter, uncertainty selection |

### What Was Built

- Earth Engine extraction scripts
- MAIAC QA masking with official bit definition
- Coverage audits (10-row, 150-row)
- QA tier validation
- Glint filter implementation
- Uncertainty-based selection

### Scientific Method Established

- Dataset: MODIS/061/MCD19A2_GRANULES
- AOD band: Optical_Depth_055 (scale: 0.001)
- Uncertainty: AOD_Uncertainty (scale: 0.0001)
- Strict QA: cloud_mask=1, land_mask=0, AOD_QA=0, glint_mask=0

---

## Stage 3: Batch Extraction Architecture

**Status:** COMPLETED
**Commits:** b54bbea to 3674808

### Key Commits

| Commit | Description |
|--------|-------------|
| b54bbea | Batched Earth Engine MAIAC extraction - 50 station-day test |
| 350d526 | Batched Earth Engine MAIAC extraction - 500 station-day test |
| 78e46c4 | Fix selection bug and prepare full 2025 MAIAC extraction |
| 3674808 | Remove getInfo() memory bug from extraction script |

### Problem Solved

Previous architecture caused "User memory limit exceeded" error
when retrieving large FeatureCollection through getInfo().

### Solution Implemented

- Small station-day batches
- Server-side FeatureCollection
- Earth Engine table export
- Persistent batch output
- Local merge

### Current Architecture

```
CPCB eligible station/dates
    |
    v
batch selection
    |
    v
Earth Engine server-side extraction
    |
    v
table export
    |
    v
local retrieval
    |
    v
local merge
    |
    v
Parquet
```

---

## Stage 4: Full 2025 MAIAC Dataset

**Status:** COMPLETED
**Commits:** f33f3a8

### Key Commit

| Commit | Description |
|--------|-------------|
| f33f3a8 | Complete full 2025 MAIAC extraction |

### Extraction Results

| Metric | Value |
|--------|-------|
| Total eligible station-days | 2737 |
| Total extracted | 2737 |
| Strict AOD valid | 596 |
| Strict AOD coverage | 21.8% |
| Research QA=11 valid | 0 |
| Failed batches | 0 |
| Runtime | ~350 seconds |

### Output Files

**File:** `data/curated/air_quality/ahmedabad_pm25_maiac_station_day_2025.parquet`
**Rows:** 2737

---

## Stage 5: ERA5 Pilot + 500-Row Model

**Status:** COMPLETED
**Commits:** 96962e2

### Key Commit

| Commit | Description |
|--------|-------------|
| 96962e2 | Implement 500-row PM2.5 pilot model with ERA5 extraction and LOSO validation |

### What Was Built

- ERA5 meteorological data extraction for pilot rows
- 500-row stratified pilot dataset
- Ridge, Random Forest, Gradient Boosting models
- Leave-One-Station-Out (LOSO) validation
- Naive baseline comparison

### Current Outputs

| File | Rows | Description |
|------|------|-------------|
| `ahmedabad_pm25_station_day_2025_pilot_500.parquet` | 500 | Pilot dataset |
| `ahmedabad_pm25_era5_pilot_500.csv` | 1728 | ERA5 data |
| `pm25_pilot_500_results.csv` | 9 | Model results |

---

## Stage 6: Baseline Freeze

**Status:** COMPLETED
**Commits:** 179a074

### Key Commit

| Commit | Description |
|--------|-------------|
| 179a074 | Freeze baseline and resolve data version discrepancy |

### What Was Done

- Baseline results frozen (do not overwrite)
- Data version discrepancy resolved (2737 vs 2780)
- Old driver CSV preserved for provenance
- Experiment tracking CSV created

---

## Stage 7: Documentation Synchronization

**Status:** COMPLETED
**Commits:** 8dcb853

### Key Commit

| Commit | Description |
|--------|-------------|
| 8dcb853 | Synchronize PM2.5 data and model documentation |

### What Was Done

- Documentation hierarchy created
- Canonical documents established
- Historical documents marked
- Decision records created
- Documentation governance established

---

## Current Project State

| Component | Status | Canonical File |
|-----------|--------|----------------|
| PM2.5 Target | COMPLETED | `ahmedabad_pm25_station_day_2025.parquet` |
| MAIAC AOD | COMPLETED | `ahmedabad_pm25_maiac_station_day_2025.parquet` |
| ERA5 Meteorology | COMPLETED | `ahmedabad_pm25_era5_pilot_500.csv` |
| 500-Row Pilot | COMPLETED | `ahmedabad_pm25_station_day_2025_pilot_500.parquet` |
| Baseline Model | FROZEN | `pm25_pilot_500_results.csv` |
| Documentation | SYNCHRONIZED | `docs/` |

---

**Status:** CANONICAL - This document traces the project's evolution using Git history.
