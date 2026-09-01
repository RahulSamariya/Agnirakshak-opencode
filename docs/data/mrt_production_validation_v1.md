# MRT Production Validation Report v1

## 1. Production method

**ECMWF thermofeel-consistent MRT**

Method version: `ECMWF_THERMOFEEL_COMPATIBLE_V1`

Implementation: `scientific/thermal_comfort/mrt.py`

## 2. Why thermofeel was selected

ECMWF documentation identifies thermofeel as the recommended methodology for
future thermal-comfort calculations. Selection criteria:

- **Source provenance**: ECMWF official library
- **Reproducibility**: deterministic, no external dependencies beyond ERA5
- **Maintainability**: maintained by ECMWF, well-documented
- **Current methodology**: reflects latest ECMWF approach
- **Compatibility**: works with available ERA5 inputs

## 3. Source implementation inspected

- **thermofeel version**: 2.3.0
- **Installation**: `pip install thermofeel`
- **Path**: `C:\Users\DELL\AppData\Local\Programs\Python\Python314\Lib\site-packages\thermofeel`
- **Key function**: `calculate_mean_radiant_temperature` (thermofeel.py:235-281)
- **dsrp helper**: `approximate_dsrp` (thermofeel.py:188-211)

## 4. Input contract

| Variable | Description | Units | Source |
|----------|-------------|-------|--------|
| ssrd | Surface solar radiation downwards | W/m2 | ERA5 |
| strd | Surface thermal radiation downwards | W/m2 | ERA5 |
| fdir | Direct solar radiation at surface | W/m2 | ERA5 |
| ssr | Surface net solar radiation | W/m2 | ERA5 |
| str | Surface net thermal radiation | W/m2 | ERA5 |

Accumulation: 1 hour (3600 seconds) verified from NetCDF metadata.

## 5. Radiation handling

- All inputs converted from J/m2 to W/m2 by dividing by accumulation_seconds
- No mixing of radiation products
- Single-source ERA5 radiation dataset used

## 6. Solar geometry

- Solar declination: Eq 8 from Di Napoli et al. (2020)
- Time correction: Eq 10 from Di Napoli et al. (2020)
- Hour angle: Eq 9 from Di Napoli et al. (2020)
- Solar zenith angle: Eq 6 from Di Napoli et al. (2020)
- **cossza = cos(zenith)** (instantaneous, thermofeel convention)

## 7. Direct solar treatment

```python
# thermofeel convention
if cossza > 0.1:
    dsrp = fdir / cossza
else:
    dsrp = fdir
```

## 8. f_p

```python
# thermofeel convention: gamma = elevation (not zenith)
gamma = elevation
f_p = 0.308 * cos(gamma * (0.998 - gamma^2/50000))
```

## 9. alpha_ir/epsilon_p

```python
# thermofeel convention: fp*dsrp INSIDE multiplier
alpha_ratio = 0.7 / 0.97
rf = 0.5*strd + 0.5*L_up + alpha_ratio * (0.5*S_diff + 0.5*S_up + fp*dsrp)
```

## 10. Nighttime handling

- When `elevation < 0`: dsrp = 0, f_p = 0
- MRT computed from longwave terms only

## 11. Thermofeel parity

| Metric | Value |
|--------|-------|
| N | 9 |
| Max absolute difference | 0.000000 K |
| Median absolute difference | 0.000000 K |
| P95 absolute difference | 0.000000 K |

**EXACT PARITY ACHIEVED** — Our implementation produces numerically identical results to ECMWF thermofeel 2.3.0 under identical inputs.

## 12. ERA5-HEAT comparison

| Metric | Value |
|--------|-------|
| N | 1488 |
| MAE | 2.27 K |
| RMSE | 3.53 K |
| Bias | +1.18 K |
| Median AE | 0.91 K |
| P95 AE | 7.45 K |
| R² | 0.970 |

Interpretation: Production methodology is thermofeel-consistent. ERA5-HEAT differences reflect methodology/reference-product distinction.

## 13. Three-way comparison

| Comparison | N | MAE | RMSE | Bias |
|------------|---|-----|------|------|
| OURS vs THERMOFEEL | 9 | 0.000 K | 0.000 K | 0.000 K |
| THERMOFEEL vs ERA5-HEAT | 124 | 2.34 K | 3.71 K | +1.67 K |
| OURS vs ERA5-HEAT | 1488 | 2.27 K | 3.53 K | +1.18 K |

Interpretation:
- Our implementation matches thermofeel (EXACT PARITY)
- Thermofeel differs from ERA5-HEAT (expected methodology distinction)
- The difference is NOT an implementation error

## 14. Limitations

- ERA5-HEAT uses different methodology (expected)
- Simplified solar geometry (no atmospheric refraction)
- Fixed clothing/body parameters (ALPHA_IR=0.7, EPSILON_P=0.97)
- Single accumulation period (1 hour)

## 15. Final scientific conclusion

Production MRT is now thermofeel-consistent. Under identical inputs, our implementation produces numerically identical results to ECMWF thermofeel 2.3.0 (max difference: 0.000000 K). The ERA5-HEAT comparison (MAE=2.27 K) reflects an expected methodology/reference-product distinction, not an implementation error.
