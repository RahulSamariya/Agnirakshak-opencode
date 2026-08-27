# Exposure Model

## Overview

The exposure model calculates population exposure using the Best-Worst Method (BBWM).

## Factor Weights

| Factor | Weight |
|--------|--------|
| Infrastructure/Transit | 28.2% |
| Fluid Intake/Activity | 28.2% |
| Lifestyle | 18.4% |
| Air Quality | 12.6% |
| Healthcare Accessibility | 12.5% |

## Sub-factor Weights

### Infrastructure/Transit
| Sub-factor | Weight |
|------------|--------|
| Condition | 50.8% |
| Facilities | 49.2% |

### Lifestyle
| Sub-factor | Weight |
|------------|--------|
| Alcohol | 34.1% |
| Sleep | 23.2% |
| Tobacco | 21.8% |
| Caffeine | 20.8% |

## Residual Floor

Exposure maintains a residual floor of 0.33 to ensure baseline exposure is always represented.

## Configuration

Weights are defined in `scientific/configuration/exposure_weights.yaml`.
