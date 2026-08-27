# Hazard Model

## Overview

The hazard model calculates thermal stress using the Universal Thermal Climate Index (UTCI).

## UTCI Calculation

UTCI integrates:
- Air temperature
- Relative humidity
- Wind speed
- Mean radiant temperature

## Hazard Categories

| UTCI Range | Category | Hazard Index |
|------------|----------|--------------|
| 9–26°C | No thermal stress | 0.00–0.25 |
| 26–32°C | Moderate heat stress | 0.25–0.50 |
| 32–38°C | Strong heat stress | 0.50–0.75 |
| 38–46°C | Very strong heat stress | 0.75–1.00 |
| >46°C | Extreme heat stress | 1.00 |

## Normalization

Within each category, linear interpolation is used between category boundaries.

## Configuration

Hazard categories are defined in `scientific/configuration/hazard_categories.yaml`.
