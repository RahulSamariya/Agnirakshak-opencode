# MAIAC 2025 Extraction

**Status:** CANONICAL
**Version:** 2.0
**Generated:** 2025-01-01
**Updated:** 2026-09-09T19:34:30.136813
**Supersedes:** Previous MAIAC documentation

---

## Section A: Method Development / 10-Row Validation

**Status:** HISTORICAL

Early validation used 10 station-day samples to verify:
- Earth Engine authentication
- MAIAC collection access
- QA band interpretation
- AOD scaling factors

**Result:** Method validated, extraction pipeline confirmed.

---

## Section B: Expanded 150-Row QA Coverage Audit

**Status:** HISTORICAL

Expanded audit used 150 stratified samples to verify:
- Strict QA coverage ~31%
- Seasonal variation in AOD availability
- QA=11 research-quality observations = 0

**Result:** AOD confirmed as sparse auxiliary predictor.

---

## Section C: Full 2025 Extraction

**Status:** CANONICAL

### Extraction Parameters

**Dataset:** MODIS/061/MCD19A2_GRANULES

**Band:** Optical_Depth_055

**Scale:** 0.001

**Uncertainty band:** AOD_Uncertainty (scale: 0.0001)

**QA field:** AOD_QA

### Strict QA Rule

```
cloud_mask = 1
land_mask = 0
AOD_QA = 0
glint_mask = 0
```

### Multiple Valid Candidates

When multiple valid candidates overlap the same station/date:
1. Apply QA first
2. Exclude glint
3. Retain valid AOD
4. Use the LOWEST valid AOD_Uncertainty

### Extraction Results

| Metric | Value |
|--------|-------|
| Total eligible station-days | 2737 |
| Total extracted | 2737 |
| Strict AOD valid | 596 |
| Strict AOD coverage | 21.8% |
| Research QA=11 valid | 0 |
| Research QA=11 coverage | 0% |
| Failed batches | 0 |
| Runtime | ~350 seconds |

### Output Files

| File | Description |
|------|-------------|
| `data/curated/air_quality/ahmedabad_pm25_maiac_station_day_2025.parquet` | Full 2025 MAIAC dataset |
| `data/staging/earth_engine/maiac_2025_batch_001.csv` | Batch 1 |
| `data/staging/earth_engine/maiac_2025_batch_002.csv` | Batch 2 |
| `data/staging/earth_engine/maiac_2025_batch_003.csv` | Batch 3 |
| `data/staging/earth_engine/maiac_2025_batch_004.csv` | Batch 4 |
| `data/staging/earth_engine/maiac_2025_batch_005.csv` | Batch 5 |
| `data/staging/earth_engine/maiac_2025_batch_006.csv` | Batch 6 |

### Scientific Interpretation

- MAIAC strict AOD is a **sparse auxiliary predictor**
- It is **NOT mandatory** for every PM2.5 row
- AOD should be treated as **OPTIONAL/AUXILIARY**
- Do not throw away CPCB/ERA5 rows because AOD is missing

---

## QA Rules (Current)

### Primary Strict Rule

```python
cloud_mask == 1
land_mask == 0
AOD_QA == 0
glint_mask == 0
```

### AOD Values

- AOD = 0 means best quality
- AOD = Optical_Depth_055 x 0.001

### QA=11 Research Quality

- Retained as separate research-quality tier
- Do NOT mix into strict_aod_550
- QA 3/4 may be retained only as diagnostics

### Do NOT Use

- first()
- unmasked mosaic()
- highest uncertainty
- neighborhood substitution

---

**Status:** CANONICAL - This is the authoritative MAIAC extraction document.
