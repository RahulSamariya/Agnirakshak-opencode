# Canonical 2025 PM2.5 Target Version

**Generated:** 2026-09-09T19:08:11.358520

---

## Data Version Reconciliation

### Discrepancy Found

| Source | Count |
|--------|-------|
| Parquet eligible (current) | 2780 |
| Driver CSV (old) | 2737 |
| Difference | 43 |

### Root Cause

The driver CSV was created from an earlier version of the CPCB data.
The current parquet contains 43 additional eligible
station-days for Maninagar (site_308) that were not in the old driver CSV.

This is a DATA UPDATE, not a processing error. The parquet reflects
the most current CPCB CAAQMS data.

### Resolution

1. Old driver file preserved for provenance:
   `data/staging/earth_engine/ahmedabad_pm25_station_days_2025_old.csv`

2. Canonical driver table updated from parquet:
   `data/staging/earth_engine/ahmedabad_pm25_station_days_2025.csv`

### Canonical Source

**The canonical 2025 target is:**
`data/curated/air_quality/ahmedabad_pm25_station_day_2025.parquet`

This file contains:
- Total station-days: 3285
- Eligible station-days: 2780
- Stations: 9
- Date range: 2025-01-01 to 2025-12-31

### Station Counts (Canonical)

| Station | Eligible Days |
|---------|---------------|
| site_308 | 351 |
| site_5449 | 231 |
| site_5450 | 308 |
| site_5451 | 325 |
| site_5452 | 292 |
| site_5453 | 351 |
| site_5454 | 288 |
| site_5455 | 306 |
| site_5456 | 328 |

### Verification

- All eligible rows have daily_qc_flag = 'ELIGIBLE'
- Minimum 18 valid hourly observations per day
- No target imputation
- Source provenance preserved

---

**Status:** CANONICAL VERSION DOCUMENTED
