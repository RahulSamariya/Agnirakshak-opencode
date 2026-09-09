# ADR 001: 2025 Target Version

**Status:** ACCEPTED
**Date:** 2026-09-09

---

## Decision

Use the parquet file as the canonical 2025 PM2.5 target source,
with 2780 eligible station-days.

## Reason

The parquet file contains the most current CPCB CAAQMS data,
including 43 additional Maninagar station-days not present in
the old driver CSV.

## Alternatives Considered

1. Use old driver CSV (2737 rows) - Rejected: Outdated data
2. Merge both sources - Rejected: Would create duplicates

## Evidence

- Parquet: 2780 eligible rows
- Driver CSV: 2737 rows
- Difference: 43 Maninagar station-days
- Old driver preserved for provenance

## Current Status

ACCEPTED - Canonical version is 2780 rows.

## Consequences

- All modeling uses 2780-row canonical source
- Old driver preserved for provenance
- Version metadata documented

---

**Supersedes:** N/A
**Superseded by:** N/A
