# TEST 2E — MRT THERMOFEEL RECONCILIATION

## Thermofeel version/source

- Version: 2.3.0
- Source: ECMWF thermofeel (pip install thermofeel)
- MRT function: `calculate_mean_radiant_temperature` (thermofeel.py lines 235-281)
- Reference: Di Napoli et al. (2020) DOI:10.1007/s00484-020-01900-5

## Input mapping

| Input | ERA5 variable | Units | Thermofeel expectation | Our usage |
|---|---|---|---|---|
| ssrd | ssrd | W/m2 (J/m2 / 3600) | Surface solar radiation downwards | Same |
| ssr | ssr | W/m2 | Surface net solar radiation | Same |
| fdir | fdir | W/m2 | Direct solar radiation at surface | Same |
| strd | strd | W/m2 | Surface thermal radiation downwards | Same |
| strr | str | W/m2 | Surface net thermal radiation | Same |
| dsrp | computed | W/m2 | Direct solar radiation perpendicular to beam | Not used directly |
| cossza | computed | dimensionless | Cosine of solar zenith angle | Same |

### Critical: dsrp computation

thermofeel: `dsrp = fdir / cossza` (when cossza > 0.1)
Our implementation: `I* = fdir / cos(theta_bar_0)` (interval-average cosine)

## Solar geometry comparison

| Quantity | Ours | Thermofeel | Match |
|---|---|---|---|
| Solar declination | Same formula | Same formula | YES |
| Hour angle | Same formula | Same formula | YES |
| Solar zenith | Same formula | Same formula | YES |
| cossza | cos(zenith) | cos(zenith) | YES |
| gamma (fp) | zenith (36.87 deg) | elevation (53.13 deg) | DIFFERENT |
| fp | 0.1979 | 0.1979 | YES (numerically equivalent) |

NOTE: gamma differs (zenith vs elevation) but fp yields the same numerical result because cos(gamma_ours * ...) = cos(gamma_thermo * ...) for the fp formula.

## Direct-solar comparison

| Quantity | Ours | Thermofeel | Difference |
|---|---|---|---|
| fdir | 654.31 W/m2 | 654.31 W/m2 | 0 |
| cossza | 0.800 | 0.800 | 0 |
| cos_bar (interval avg) | 0.748 | N/A | N/A |
| dsrp | N/A | 817.90 W/m2 | N/A |
| I* | 874.40 W/m2 | N/A | N/A |
| I*/dsrp ratio | 1.069 | 1.000 | +6.9% |

## MRT term-by-term comparison (06:00 UTC, elev=53.1 deg)

| Term | OURS | THERMOFEEL | Diff |
|---|---|---|---|
| L_srf_dn (strd) | 343.41 | 343.41 | 0.00 |
| L_srf_up (lur) | 510.00 | 510.00 | 0.00 |
| S_diffuse (dsw) | 128.85 | 128.85 | 0.00 |
| S_reflected (rsw) | 151.64 | 151.64 | 0.00 |
| I*/dsrp | 874.40 | 817.90 | +56.51 |
| fp | 0.1979 | 0.1979 | 0.00 |
| f_a*L_d | 171.71 | 171.71 | 0.00 |
| f_a*L_u | 255.00 | 255.00 | 0.00 |
| ar*f_a*S_d | 46.49 | 46.49 | 0.00 |
| ar*f_a*S_u | 54.72 | 54.72 | 0.00 |
| fp*I*/fp*dsrp term | 173.03 | 116.80 | +56.23 |
| total_rf | 700.94 | 644.71 | +56.23 |
| MRT (K) | 333.45 | 326.55 | +6.90 |

### Key formula difference

thermofeel: `(0.7/0.97) * (0.5*dsw + 0.5*rsw + fp*dsrp)`
Ours: `(0.7/0.97)*0.5*dsw + (0.7/0.97)*0.5*rsw + fp*I*`

The direct solar term in thermofeel is INSIDE the (alpha_ir/epsilon_p) multiplier.
In ours, it is OUTSIDE.

## Pairwise metrics

| Comparison | N | MAE | RMSE | Bias | MedAE | P95 | R2 |
|---|---|---|---|---|---|---|---|
| OURS vs THERMOFEEL | 124 | 1.5734 | 2.9938 | 1.5652 | 0.0041 | 6.3826 | 0.980995 |
| THERMOFEEL vs ERA5-HEAT | 124 | 2.3440 | 3.7138 | 1.6687 | 1.0066 | 7.7894 | 0.967094 |
| OURS vs ERA5-HEAT | 124 | 3.2576 | 4.4711 | 3.2339 | 1.9657 | 8.1060 | 0.952303 |

## Stratified by elevation

| Bin | N | O vs T MAE | T vs E MAE | O vs E MAE |
|---|---|---|---|---|
| Night (-90,0] | 62 | 0.0000 | 0.4652 | 0.4652 |
| Low (10,25] | 31 | 0.3390 | 7.1423 | 7.4487 |
| High (50,90] | 31 | 5.9546 | 1.3032 | 4.6514 |

## Nighttime comparison

All three implementations agree at nighttime:
- OURS = 280.50 K
- THERMOFEEL = 280.50 K
- ERA5-HEAT = 280.26 K
- O-T = 0.00 K, T-E = 0.24 K, O-E = 0.24 K

Nighttime conventions are equivalent across all three.

## Low-solar comparison

At low solar elevation (15.7 deg):
- OURS = 330.55 K, THERMOFEEL = 330.74 K, ERA5-HEAT = 322.47 K
- O-T = -0.20 K (nearly identical)
- T-E = +8.27 K (both much higher than ERA5-HEAT)

Both OURS and THERMOFEEL use large dsrp/I* values at low sun, producing similar MRT.

## Root-cause analysis

**SOURCE FACT**: thermofeel uses `dsrp = fdir / cossza` (instantaneous perpendicular radiation) multiplied by `(alpha_ir/epsilon_p)` inside the MRT formula. Our implementation uses `I* = fdir / cos(theta_bar_0)` (interval-average cosine) NOT multiplied by `(alpha_ir/epsilon_p)`.

**OBSERVED RESULT**: At high solar elevation, dsrp (instantaneous) < I* (interval average), but thermofeel multiplies by `(alpha_ir/epsilon_p)=0.722` while ours does not, creating opposing effects. Net result: OURS > THERMOFEEL by ~6.9 K at high sun.

**OBSERVED RESULT**: At low solar elevation, dsrp ≈ I* and the (alpha_ir/epsilon_p) multiplier partially offsets, making O-T small (~0.2 K).

**INFERENCE**: The difference between OURS and THERMOFEEL is due to TWO distinct implementation differences:
1. dsrp (instantaneous) vs I* (interval average)
2. (alpha_ir/epsilon_p) multiplier placement on the direct solar term

**INFERENCE**: Both OURS and THERMOFEEL differ from ERA5-HEAT because ERA5-HEAT uses a different methodology (likely the original Di Napoli formulation with different preprocessing conventions).

## Production-code decision

The reconciliation reveals two legitimate implementation differences between our code and thermofeel. Neither is clearly an "error" — they represent different interpretations of the same paper. The thermofeel implementation is the ECMWF reference.

**RECOMMENDATION**: Align our MRT formula with thermofeel's structure by:
1. Moving `(alpha_ir/epsilon_p)` to multiply ALL shortwave terms (including fp*dsrp)
2. Using instantaneous dsrp = fdir / cossza instead of interval-average I*

This would make our implementation consistent with the ECMWF reference.

**MODIFIED = YES** (recommendation only, pending user approval)

## Limitations

- Only 124 timestamps analyzed (March 2010, single grid point)
- ERA5-HEAT methodology is not fully documented in public sources
- thermofeel does not handle accumulation intervals (instantaneous only)
- The paper's Eq. 13 interpretation remains ambiguous

## Conclusion

**Root cause**: MULTIPLE DIFFERENCES
- Implementation difference in direct solar projection (dsrp vs I*)
- Implementation difference in alpha_ir/epsilon_p multiplier placement
- ERA5-HEAT uses a different methodology from both

**Scientific conclusion**: Our implementation faithfully follows the Di Napoli paper's equations but differs from ECMWF's operational implementation. The thermofeel code represents the authoritative ECMWF interpretation.

---

**Version:** 1.0 (TEST 2E)
**Date:** 2026-09-01
