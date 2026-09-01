# MRT Production Method v1

## Selected methodology

**ECMWF thermofeel-consistent MRT**

Method version: `ECMWF_THERMOFEEL_COMPATIBLE_V1`

## Why thermofeel was selected

ECMWF documentation identifies thermofeel as the recommended methodology for
future thermal-comfort calculations. The production implementation is chosen
based on:

- **Source provenance**: ECMWF official library (thermofeel 2.3.0)
- **Reproducibility**: deterministic, no external data dependencies beyond ERA5
- **Maintainability**: maintained by ECMWF, well-documented
- **Current methodology**: reflects latest ECMWF approach
- **Compatibility**: works with available ERA5 inputs

Do NOT choose a methodology because it gives the smallest error against
ERA5-HEAT. ERA5-HEAT is an external reference dataset, not the implementation
target.

## Production implementation

### Reference

Di Napoli, Hogan, Pappenberger (2020)
"Mean radiant temperature from global-scale numerical weather prediction models"
DOI: 10.1007/s00484-020-01900-5

### Implementation standard

ECMWF thermofeel 2.3.0 (`calculate_mean_radiant_temperature`)

### Constants

| Constant | Value | Source |
|----------|-------|--------|
| SIGMA | 5.67e-8 | Stefan-Boltzmann constant |
| F_A | 0.5 | Angle factor for upper/lower hemispheres |
| ALPHA_IR | 0.7 | Solar absorption coefficient of clothed human body |
| EPSILON_P | 0.97 | Emissivity of clothed human body |
| DSRP_COSZ_THRESHOLD | 0.1 | Minimum cossza for dsrp = fdir/cossza |

### Input variables

| Variable | Description | Units |
|----------|-------------|-------|
| ssrd | Surface solar radiation downwards | W/m2 |
| strd | Surface thermal radiation downwards | W/m2 |
| fdir | Direct solar radiation at surface | W/m2 |
| ssr | Surface net solar radiation | W/m2 |
| str | Surface net thermal radiation | W/m2 |

### Derived quantities

```
L_srf_up = strd - str              (Eq 3: upward longwave)
S_diffuse = ssrd - fdir            (Eq 4: diffuse shortwave)
S_srf_up = ssrd - ssr              (Eq 5: upward shortwave reflected)
```

### Solar geometry

- Solar declination: Eq 8 from Di Napoli et al.
- Time correction: Eq 10 from Di Napoli et al.
- Hour angle: Eq 9 from Di Napoli et al.
- Solar zenith angle: Eq 6 from Di Napoli et al.
- `cossza = cos(zenith)` (instantaneous)

### Direct solar treatment (thermofeel convention)

```
dsrp = fdir / cossza    (where cossza > 0.1)
dsrp = fdir             (where cossza <= 0.1)
```

### Surface projection factor f_p (Eq 15)

```
gamma = elevation   (thermofeel convention: elevation, not zenith)
f_p = 0.308 * cos(gamma * (0.998 - gamma^2/50000))
```

### alpha_ir/epsilon_p treatment (thermofeel convention)

```
alpha_ratio = ALPHA_IR / EPSILON_P = 0.7 / 0.97

rf = F_A * strd + F_A * L_srf_up
   + alpha_ratio * (F_A * S_diffuse + F_A * S_srf_up + f_p * dsrp)
```

Note: `f_p * dsrp` is INSIDE the `(alpha_ir/epsilon_p)` multiplier.

### MRT calculation

```
MRT = (rf / SIGMA)^0.25
```

### Nighttime handling

- When `elevation < 0`: `dsrp = 0`, `f_p = 0`
- MRT computed from longwave terms only

### Quality flags

| Flag | Value | Description |
|------|-------|-------------|
| VALID | 0 | Normal daytime calculation |
| NIGHTTIME | 1 | Solar elevation <= 0 |
| LOW_SOLAR_ELEVATION | 2 | Solar elevation < 2 degrees |
| NEGATIVE_RADIATION | 3 | Radiant flux < 0 |
| MISSING_INPUT | 4 | NaN in input data |
| MRT_UNPHYSICAL | 5 | MRT outside [150, 400] K |

## What differs from ERA5-HEAT

ERA5-HEAT uses an older operational methodology that differs from thermofeel in:

1. **Direct solar treatment**: ERA5-HEAT may use different accumulation conventions
2. **Formula structure**: ERA5-HEAT may apply alpha_ir/epsilon_p differently
3. **Reference product**: ERA5-HEAT is a processed product, not raw calculations

These are expected methodology/reference-product distinctions.

## What is validated

- Numerical parity with ECMWF thermofeel 2.3.0 under identical inputs
- Physical sanity checks (albedo, longwave, shortwave ranges)
- Quality flag coverage
- Nighttime behavior

## What is not validated

- Comparison with ERA5-HEAT (reported separately as independent reference)
- Performance under extreme conditions (polar, desert)
- Sub-daily variability at time scales < 1 hour

## Limitations

- Uses simplified solar geometry (no atmospheric refraction)
- Assumes uniform sky conditions (no cloud fraction weighting)
- Fixed clothing/body parameters (ALPHA_IR, EPSILON_P)
- Single accumulation period (1 hour for ERA5)

## Files

- `scientific/thermal_comfort/mrt.py` — Production MRT module
- `tests/scientific_validation/test_mrt.py` — Regression tests
- `docs/data/mrt_production_method_v1.md` — This document
- `data/profiles/mrt_production_validation_v1.json` — Validation JSON
- `data/curated/mrt_march_2010.parquet` — Curated dataset
