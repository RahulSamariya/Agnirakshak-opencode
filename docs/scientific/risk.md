# Risk Model

## Overview

The risk model calculates the Human Thermal Stress Risk Index (HSRI).

## Formula

```
HSRI = H × V × E
```

Where:
- **H** = Hazard Index (0.0 - 1.0)
- **V** = Vulnerability Index (0.0 - 1.0)
- **E** = Exposure Index (0.0 - 1.0)

## Risk Categories

| HSRI Range | Category |
|------------|----------|
| 0 < HSRI ≤ 0.33 | LOW |
| 0.33 < HSRI ≤ 0.66 | MEDIUM |
| 0.66 < HSRI ≤ 1.00 | HIGH |

## Special Cases

- If H = 0, then HSRI = 0 (no hazard = no risk)
- V and E retain their residual floor (0.33) even when low

## Explainability

Every risk assessment must be explainable in terms of:
- UTCI value
- Hazard Index and Category
- Vulnerability Index and top contributing factors
- Exposure Index and top contributing factors
- Model version and calculation metadata

## Configuration

Risk thresholds are defined in `scientific/configuration/risk_thresholds.yaml`.
