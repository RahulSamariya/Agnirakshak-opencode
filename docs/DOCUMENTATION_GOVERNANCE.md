# Documentation Governance

**Status:** CURRENT
**Version:** 1.0
**Generated:** 2026-09-09T19:34:30.191094

---

## Rules

1. **Actual files/data beat old Markdown claims.**
   If documentation and actual data disagree, actual data wins.

2. **One canonical document per major dataset/model.**
   - PM2.5 data: `docs/data/ahmedabad_pm25_2025_canonical.md`
   - Model baseline: `docs/models/pm25_pilot_2025_baseline.md`
   - MAIAC method: `docs/data/maiac_2025_extraction.md`

3. **Historical documents are never silently treated as current.**
   Must have clear HISTORICAL/SUPERSEDED header.

4. **Data version changes require explicit version notes.**
   Document in `data/metadata/canonical_2025_target_version.md`.

5. **Model metrics must reference the exact dataset version.**
   Include dataset version in all model reports.

6. **Scientific methodology changes require a decision record.**
   Create ADR in `docs/decisions/`.

7. **No synthetic data may enter canonical datasets.**
   All values must come from actual observations.

8. **Reproducibility paths must point to actual files/scripts.**
   No placeholder paths.

9. **Every current numerical claim must be traceable to a dataset or
   result artifact.**
   Include source file path for all numbers.

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

## Document Headers

Every document must have:

```
**Status:** [CANONICAL|CURRENT|HISTORICAL|SUPERSEDED|EXPERIMENTAL]
**Version:** X.Y
**Generated:** YYYY-MM-DD
**Updated:** YYYY-MM-DD
**Supersedes:** [document or N/A]
**Superseded by:** [document or N/A]
```

---

## Version Control

- All documentation changes must be committed
- Commit messages must reference documentation type
- Historical documents must not be deleted

---

**Status:** CURRENT - This governance document is authoritative.
