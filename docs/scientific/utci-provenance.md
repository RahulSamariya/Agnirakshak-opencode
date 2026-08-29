# UTCI Implementation Provenance

## Implementation Method

The UTCI is calculated using the **6th-degree polynomial regression approximation** from Bröde et al. (2012), which approximates the full Fiala et al. (2012) multi-node thermoregulation model.

## Source / Library

- **Polynomial coefficients:** Exact coefficient set from `pythermalcomfort` (BSD-3 licensed)
- **Reference:** Fiala D, Havenith G, Bröde P, Kampmann B, Jendritzky G. (2012). UTCI-Fiala multi-node model of human heat transfer and temperature regulation. Int J Biometeorol. 56:429-441.
- **Validation:** Cross-validated against the standalone `utci` PyPI package (exact numerical translation from reference Fortran implementation)

## Input Units

| Parameter | Unit | Valid Range |
|-----------|------|-------------|
| Air temperature (Ta) | C | -50 to +50 |
| Mean radiant temperature (Tmrt) | C | Ta-30 to Ta+70 |
| Wind speed at 10m (v) | m/s | 0.5 to 17.0 |
| Relative humidity (RH) | % | 0 to 100 |
| Water vapour pressure (VP) | hPa | <= 50 |

## Conversion Rules

- Vapour pressure: Calculated from Ta and RH using the exponential formula from pythermalcomfort (natural logarithm variant)
- Internal: VP converted from hPa to kPa before entering the polynomial
- Output: UTCI in Celsius, rounded to 1 decimal place

## Valid Ranges

The polynomial is valid for:
- Ta: -50 to +50 C
- Tmrt: Ta - 30 to Ta + 70 C
- v: 0.5 to 17.0 m/s
- VP: 0 to 50 hPa

Results outside these ranges may be unreliable. The implementation raises `ValueError` for out-of-range inputs.

## Distinguishing Scientific Standard vs Implementation

| Aspect | Description |
|--------|-------------|
| **Scientific standard** | UTCI defined by Fiala et al. (2012) multi-node model |
| **Software implementation** | 210-coefficient polynomial regression from Bröde et al. (2012) |
| **Project wrapper** | `UTCICalculatorModel` class implementing `ThermalComfortModel` ABC |

## Reference Test Cases

| Case | Ta | Tmrt | v | RH/VP | Our UTCI | Prompt Expected | Discrepancy | Source |
|------|-----|------|---|-------|----------|-----------------|-------------|--------|
| 1 | 30 | 30 | 0.5 | RH=50% | 30.4 | ~32.2 | -1.8 | Prompt approximate |
| 2 | 29 | 29 | 0.5 | VP=20hPa | 29.2 | ~29.0 | +0.2 | Prompt approximate |
| 3 | 30 | 35 | 1.0 | RH=70% | 33.5 | 38.0-39.5 | -5.0 | Prompt approximate |
| 4 | 0 | 0 | 5.0 | RH=50% | -14.7 | ~-10.0 | -4.7 | Prompt approximate |

**Note:** Our implementation exactly matches the reference Fortran-derived `utci` PyPI package. The prompt values are approximate and do not match any standard UTCI implementation. No modification was made to the UTCI formula to force agreement with approximate reference values.
