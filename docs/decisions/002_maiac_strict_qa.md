# ADR 002: MAIAC Strict QA

**Status:** ACCEPTED
**Date:** 2026-09-09

---

## Decision

Use strict QA filtering for MAIAC AOD:
- cloud_mask = 1
- land_mask = 0
- AOD_QA = 0
- glint_mask = 0

## Reason

Ensures highest quality AOD observations for modeling.
Reduces noise from cloud contamination and surface glint.

## Alternatives Considered

1. Use all AOD values - Rejected: Too much noise
2. Use QA=11 research quality - Rejected: Insufficient coverage
3. Use neighborhood mean - Rejected: Not direct observation

## Evidence

- Strict AOD coverage: 21.8%
- QA=11 coverage: 0%
- Multiple valid candidates: Select lowest uncertainty

## Current Status

ACCEPTED - Strict QA is the standard.

## Consequences

- AOD is sparse (21.8% coverage)
- Must treat AOD as optional predictor
- Cannot require AOD for every PM2.5 row

---

**Supersedes:** N/A
**Superseded by:** N/A
