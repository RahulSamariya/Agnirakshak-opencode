# ADR 003: MAIAC Batch Export Architecture

**Status:** ACCEPTED
**Date:** 2026-09-09

---

## Decision

Use batch export architecture for MAIAC extraction:
- Small station-day batches
- Server-side FeatureCollection
- Earth Engine table export
- Persistent batch output
- Local merge

## Reason

Previous architecture caused "User memory limit exceeded" error
when retrieving large FeatureCollection through getInfo().

## Alternatives Considered

1. Large FeatureCollection getInfo() - Rejected: Memory limit
2. Full-city daily rasters - Rejected: Too slow
3. Single batch export - Rejected: Still too large

## Evidence

- Previous error: "User memory limit exceeded"
- Batch architecture: 0 failed batches
- Runtime: ~350 seconds for full 2025

## Current Status

ACCEPTED - Batch architecture is the standard.

## Consequences

- Extraction completes successfully
- No memory errors
- Reproducible pipeline

---

**Supersedes:** N/A
**Superseded by:** N/A
