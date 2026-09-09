# PM2.5 Pilot Model Report (500-Row)

**Generated:** 2026-09-09T18:50:57.172683
**Status:** PILOT MODEL (not final/production)

---

## 1. Dataset Summary

| Metric | Count |
|--------|-------|
| Total Pilot Rows | 500 |
| ERA5-Complete Rows | 500 |
| AOD-Complete Rows | 92 |
| Fully Complete Rows | 92 |
| Stations | 9 |

**Stations:** Maninagar, SVPS Stadium, Gyaspur, Rakhial, Raikhad, Chandkheda, SAC ISRO Bopal, SAC ISRO Satellite, SVPI Airport Hansol

---

## 2. Model A — ERA5 Only

### A1: All Eligible Rows (500 rows)

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
| Ridge | 14.56 +/- 3.71 | 18.72 +/- 5.06 | 0.335 +/- 0.272 | -0.00 +/- 6.19 |
| RandomForest | 12.17 +/- 3.74 | 15.75 +/- 4.54 | 0.500 +/- 0.285 | 0.37 +/- 5.44 |
| GradientBoosting | 12.53 +/- 3.69 | 16.39 +/- 4.27 | 0.446 +/- 0.307 | 0.51 +/- 5.19 |

### A2: AOD-Available Subset (92 rows)

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
| Ridge | 15.79 +/- 6.03 | 18.72 +/- 6.45 | -0.456 +/- 0.652 | -2.82 +/- 11.39 |
| RandomForest | 17.58 +/- 6.02 | 21.27 +/- 7.06 | -0.852 +/- 0.518 | -3.97 +/- 13.70 |
| GradientBoosting | 18.96 +/- 5.76 | 23.02 +/- 6.59 | -1.170 +/- 0.423 | -3.83 +/- 15.83 |

---

## 3. Model B - ERA5 + MAIAC AOD

### B: AOD-Available Subset (92 rows)

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
| Ridge | 15.75 +/- 6.29 | 18.51 +/- 6.89 | -0.409 +/- 0.646 | -2.90 +/- 11.15 |
| RandomForest | 17.83 +/- 7.45 | 20.91 +/- 8.11 | -0.816 +/- 0.794 | -3.79 +/- 13.43 |
| GradientBoosting | 20.89 +/- 9.34 | 24.40 +/- 9.40 | -1.609 +/- 1.406 | -3.37 +/- 12.49 |

---

## 4. Matched-Subset Comparison (A2 vs B)

| Model | delta-MAE | delta-RMSE | delta-R2 |
|-------|-----------|------------|----------|
| Ridge | -0.04 | -0.21 | +0.047 |
| RandomForest | +0.25 | -0.36 | +0.036 |
| GradientBoosting | +1.93 | +1.39 | -0.439 |

**Interpretation:**
- Negative delta-MAE/RMSE = AOD improves prediction
- Positive delta-R2 = AOD improves variance explained

---

## 5. Per-Station LOSO Results (Best Model)

**Best model:** Ridge (Dataset B)

| Station | N Test | MAE | RMSE | R2 | Bias |
|---------|--------|-----|------|----|------|
| Chandkheda | 8 | 11.51 | 14.01 | -0.024 | -6.46 |
| Gyaspur | 18 | 25.20 | 27.82 | -0.261 | 14.65 |
| Maninagar | 8 | 15.98 | 17.47 | -0.448 | -8.60 |
| Raikhad | 17 | 12.89 | 16.37 | -0.051 | 5.55 |
| Rakhial | 9 | 23.03 | 26.37 | -0.759 | -20.02 |
| SAC ISRO Bopal | 9 | 10.14 | 10.86 | 0.277 | -7.47 |
| SAC ISRO Satellite | 10 | 14.95 | 18.23 | -1.781 | 10.40 |
| SVPS Stadium | 9 | 6.60 | 9.19 | 0.207 | -2.37 |
| SVPI Airport Hansol | 4 | 21.44 | 26.29 | -0.842 | -11.74 |

---

## 6. Methodology

- **Validation:** Leave-One-Station-Out (LOSO)
- **Preprocessing:** StandardScaler fitted inside each training fold
- **Features (ERA5):** temperature, RH, wind speed, surface pressure, precipitation
- **Features (AOD):** ERA5 + strict_aod_550
- **Target:** daily_pm25_ug_m3 (ug/m3)
- **No station_id, lat/lon, or target-derived features used**

---

## 7. Status

This is a **PILOT MODEL** to assess whether the modeling approach is
promising before scaling to the larger 2023-2025 dataset.

Do NOT call this a final, production, or operational model.
