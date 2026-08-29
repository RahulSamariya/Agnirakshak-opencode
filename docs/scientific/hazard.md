# Hazard Model

## Overview

The hazard model calculates thermal stress using the Universal Thermal Climate Index (UTCI).

[SOURCE-DERIVED]

## UTCI Inputs

UTCI integrates four meteorological variables:
- Air temperature (°C)
- Relative humidity (%)
- Wind speed (m/s)
- Mean radiant temperature (°C)

[SOURCE-DERIVED]

## UTCI Status

**UTCI IMPLEMENTATION BLOCKED — REFERENCE METHODOLOGY MISSING**

The supplied sources do not contain:
- A closed-form UTCI polynomial
- Regression coefficients
- Python library reference (e.g., pythermalcomfort)
- Numerical test cases for validation

The UTCI implementation must be selected and validated against authoritative reference data before implementation.

[SOURCE-DERIVED — confirmed by latest output PDF]

## Hazard Categories

| UTCI Range | Category | Hazard Index (H) |
|------------|----------|-------------------|
| 9–26°C | No thermal stress | 0.00–0.25 |
| 26–32°C | Moderate heat stress | 0.25–0.50 |
| 32–38°C | Strong heat stress | 0.50–0.75 |
| 38–46°C | Very strong heat stress | 0.75–1.00 |
| >46°C | Extreme heat stress | 1.00 |

[SOURCE-DERIVED]

## Normalization

Within each category, linear interpolation is used between category boundaries.

- Values ≤ 9°C are clamped to H = 0.0
- Values > 46°C are capped at H = 1.0

[SOURCE-DERIVED]

## Configuration

Hazard categories are defined in `scientific/configuration/hazard_categories.yaml` and validated by `HazardCategoriesConfig` in `scientific/configuration/models.py`.

[PROJECT IMPLEMENTATION CONVENTION]

## Interface

- Abstract: `scientific/hazard/base.py` → `HazardModel`
- Concrete: `scientific/hazard/utci/normalization.py` → `UTCIHazardModel`
- Normalization function: `normalize_utci(utci_c) → float`
- Category classifier: `classify_utci(utci_c) → HazardCategory`

[PROJECT IMPLEMENTATION CONVENTION]
