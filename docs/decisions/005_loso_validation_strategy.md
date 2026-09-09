# ADR 005: LOSO Validation Strategy

**Status:** ACCEPTED
**Date:** 2026-09-09

---

## Decision

Use Leave-One-Station-Out (LOSO) as primary validation method.

## Reason

Tests spatial generalization to unseen stations, which is the
primary deployment scenario.

## Alternatives Considered

1. Random train/test split - Rejected: May leak station info
2. Time-based split - Rejected: Doesn't test spatial generalization
3. K-fold cross-validation - Rejected: May mix stations

## Evidence

- 9 stations = 9 LOSO folds
- Each fold: 8 train, 1 test
- No station leakage
- Preprocessing fitted inside each fold

## Current Status

ACCEPTED - LOSO is the standard.

## Consequences

- Tests spatial generalization
- Prevents station leakage
- More conservative estimate of performance

---

**Supersedes:** N/A
**Superseded by:** N/A
