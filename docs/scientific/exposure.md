# Exposure Model

## Overview

The exposure model calculates population exposure using the Best-Worst Method (BBWM).

[SOURCE-DERIVED]

## Conceptual Distinction: H, V, E

The HSRI model distinguishes three components:

- **H (Hazard):** Thermal hazard from environmental conditions (UTCI-derived)
  - Physical exposure to heat stress
  - Determined by meteorological conditions

- **V (Vulnerability):** Susceptibility of the population
  - Demographic factors (age, gender)
  - Health factors (chronic disease, disability)
  - Socioeconomic factors (education, economic status)

- **E (Exposure):** Population exposure to heat conditions
  - Population presence in affected areas
  - Occupation and outdoor activity patterns
  - Built environment and infrastructure
  - Environmental conditions (air quality)

## Top-Level Component Weights

| Component | Weight | Source | Evidence Status |
|-----------|--------|--------|-----------------|
| Infrastructure/Transit | 28.2% | SOURCE-DERIVED | Project convention |
| Fluid Intake/Activity | 28.2% | SOURCE-DERIVED | Project convention |
| Lifestyle | 18.4% | SOURCE-DERIVED | Project convention |
| Air Quality | 12.6% | SOURCE-DERIVED | Project convention |
| Healthcare Accessibility | 12.5% | SOURCE-DERIVED | Project convention |

Note: Top-level weights sum to 0.999 (published rounded coefficients). Not renormalized.

[SOURCE-DERIVED — published values preserved]

## Sub-factor Weights

### Infrastructure/Transit

| Sub-factor | Weight | Source | Evidence Status |
|------------|--------|--------|-----------------|
| Condition | 50.8% | SOURCE-DERIVED | Project convention |
| Facilities | 49.2% | SOURCE-DERIVED | Project convention |

### Lifestyle

| Sub-factor | Weight | Source | Evidence Status |
|------------|--------|--------|-----------------|
| Alcohol | 34.1% | SOURCE-DERIVED | Project convention |
| Sleep | 23.2% | SOURCE-DERIVED | Project convention |
| Tobacco | 21.8% | SOURCE-DERIVED | Project convention |
| Caffeine | 20.8% | SOURCE-DERIVED | Project convention |

## Commuting Classification (Infrastructure/Transit sub-component)

| Commuting Type | Score | Source |
|----------------|-------|--------|
| Air-conditioned commuting | 0.33 (LOW) | SOURCE-DERIVED |
| Non-AC motorized vehicles | 0.66 (MEDIUM) | SOURCE-DERIVED |
| Non-AC non-motorized transport | 1.00 (HIGH) | SOURCE-DERIVED |

Commuting is a sub-component of Infrastructure/Transit, not a replacement for the entire Exposure model.

[SOURCE-DERIVED]

## Lifestyle Thresholds

| Factor | Threshold | Score | Source |
|--------|-----------|-------|--------|
| Sleep deficit | < 6 hours | HIGH | SOURCE-DERIVED |
| Caffeine | > 300 mg/day | HIGH | SOURCE-DERIVED |
| Tobacco | Regular use | HIGH | SOURCE-DERIVED |
| Alcohol | > 1 drinking event/quarter | HIGH | SOURCE-DERIVED |

## Air Quality

The source describes joint heat + ambient air-pollution co-exposure as high exposure.

**DO NOT invent an AQI threshold.** Mark as:

> TBD / requires scientific confirmation

[NOT YET SPECIFIED — exact AQI/PM2.5 threshold]

## Scoring Scale

| Score | Label |
|-------|-------|
| 0.33 | LOW |
| 0.66 | MEDIUM |
| 1.00 | HIGH |

[SOURCE-DERIVED]

## Residual Floor

Exposure maintains a residual floor of 0.33 to ensure baseline exposure is always represented.

[SOURCE-DERIVED]

## Raw-to-Score Classification

The source provides explicit classification rules for Commuting (Infrastructure/Transit) and Lifestyle thresholds. For other factors (Fluid Intake/Activity, Air Quality, Healthcare Accessibility), raw-to-score rules are NOT YET SPECIFIED.

Current implementation accepts pre-normalized scores (0.33/0.66/1.00).

[NOT YET SPECIFIED — Fluid Intake/Activity, Air Quality, Healthcare Accessibility classification rules]

## Configuration

Weights are defined in `scientific/configuration/exposure_weights.yaml` and validated by `ExposureWeightsConfig` in `scientific/configuration/models.py`.

[PROJECT IMPLEMENTATION CONVENTION]
