# Risk Model

## Overview

The risk model calculates the Human Thermal Stress Risk Index (HSRI).

[SOURCE-DERIVED]

## Formula

```
HSRI = H × V × E
```

[SOURCE-DERIVED]

Where:
- **H** = Hazard Index (0.0 – 1.0)
- **V** = Vulnerability Index (0.33 – 1.0, residual floor 0.33)
- **E** = Exposure Index (0.33 – 1.0, residual floor 0.33)

HSRI is NOT mortality probability. It is a normalized risk index.

[SOURCE-DERIVED]

## Risk Categories

| HSRI Range | Category | Source |
|------------|----------|--------|
| 0 < HSRI ≤ 0.33 | LOW | SOURCE-DERIVED |
| 0.33 < HSRI ≤ 0.66 | MEDIUM | SOURCE-DERIVED |
| 0.66 < HSRI ≤ 1.00 | HIGH | SOURCE-DERIVED |

## Special Cases

- If H = 0, then HSRI = 0 (no hazard = no risk)
- V and E retain their residual floor (0.33) even when low

[SOURCE-DERIVED]

## Explainability

Every risk assessment must be explainable in terms of:
- UTCI value
- Hazard Index and Category
- Vulnerability Index and top contributing factors
- Exposure Index and top contributing factors
- Model version and calculation metadata

[PROJECT IMPLEMENTATION CONVENTION]

## Configuration

Risk thresholds are defined in `scientific/configuration/risk_thresholds.yaml` and validated by `RiskThresholdsConfig` in `scientific/configuration/models.py`.

[PROJECT IMPLEMENTATION CONVENTION]

## Interface

- Abstract: `scientific/risk/base.py` → `RiskModel`
- Concrete: `scientific/risk/hsri.py` → `MultiplicativeHSRIModel`

[PROJECT IMPLEMENTATION CONVENTION]
