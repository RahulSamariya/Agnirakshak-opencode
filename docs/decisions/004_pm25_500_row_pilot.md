# ADR 004: PM2.5 500-Row Pilot

**Status:** ACCEPTED
**Date:** 2026-09-09

---

## Decision

Use 500-row stratified sample for initial pilot modeling.

## Reason

Allows rapid prototyping and method validation before scaling
to full 2780-row dataset.

## Alternatives Considered

1. Use all 2780 rows - Rejected: Too slow for iteration
2. Use 100 rows - Rejected: Too small for LOSO
3. Random sample - Rejected: May miss important patterns

## Evidence

- 500 rows: 9 stations, all months represented
- Stratified by station and month
- ERA5-complete: 500/500
- AOD-complete: 92/500

## Current Status

ACCEPTED - 500-row pilot is the standard.

## Consequences

- Rapid iteration possible
- LOSO validation feasible
- Can scale to full dataset later

---

**Supersedes:** N/A
**Superseded by:** N/A
