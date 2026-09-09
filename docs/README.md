# AGNIRAKSHAK Documentation

**Status:** CURRENT
**Last Updated:** 2026-09-09

---

## Documentation Hierarchy

### Canonical Documents (Source of Truth)

| Document | Path | Description |
|----------|------|-------------|
| PM2.5 Data | `data/ahmedabad_pm25_2025_canonical.md` | Canonical 2025 PM2.5 modeling data |
| Model Baseline | `models/pm25_pilot_2025_baseline.md` | First pilot model experiment |
| MAIAC Method | `data/maiac_2025_extraction.md` | MAIAC AOD extraction methodology |
| Target Version | `../data/metadata/canonical_2025_target_version.md` | Data version authority |

### Current Documentation

| Document | Path | Description |
|----------|------|-------------|
| Experiment Log | `../data/models/pm25_pilot_experiment_log.csv` | Model experiment tracking |
| Freeze Report | `models/pm25_pilot_freeze_report.md` | Baseline freeze documentation |

### Historical Documentation

Historical documents are retained for provenance but should NOT be
used as current implementation specifications. See `archive/README.md`
for the complete list.

### Decision Records

See `decisions/` for Architecture Decision Records (ADRs).

### Governance

See `DOCUMENTATION_GOVERNANCE.md` for documentation rules.

---

## Status Taxonomy

| Status | Definition |
|--------|------------|
| CANONICAL | Current authoritative description of actual project state |
| CURRENT | Current operational documentation, not central source of truth |
| HISTORICAL | Accurate snapshot of earlier project state |
| SUPERSEDED | Replaced by newer methodology/data |
| EXPERIMENTAL | Research/test documentation, not yet frozen |

---

**Note:** Actual files/data always beat old Markdown claims.
