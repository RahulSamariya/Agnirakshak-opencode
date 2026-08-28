# Data Flow

## Weather Pipeline

```
External Source
      │
      ▼
┌─────────────┐
│   Ingest    │  Fetch forecast/observation data          [PHASE 1: SCAFFOLD]
└─────────────┘
      │
      ▼
┌─────────────┐
│  Validate   │  Check data quality                       [PHASE 1: SCAFFOLD]
└─────────────┘
      │
      ▼
┌─────────────┐
│  Normalize  │  Convert to standard units                [PHASE 1: SCAFFOLD]
└─────────────┘
      │
      ▼
┌─────────────┐
│ Spatialize  │  Assign to grid cells                     [PHASE 1: SCAFFOLD]
└─────────────┘
      │
      ▼
┌─────────────┐
│  UTCI Calc  │  Calculate thermal comfort                [PHASE 2: PLANNED]
└─────────────┘
      │
      ▼
┌─────────────┐
│   Hazard    │  Normalize to hazard index                [PHASE 2: PLANNED]
└─────────────┘
      │
      ▼
   Storage
```

## Risk Pipeline

```
Hazard Assessments
Vulnerability Profiles
Exposure Profiles
      │
      ▼
┌─────────────┐
│  HSRI Calc  │  H x V x E                               [PHASE 2: PLANNED]
└─────────────┘
      │
      ▼
┌─────────────┐
│  Classify   │  LOW | MEDIUM | HIGH                      [PHASE 2: PLANNED]
└─────────────┘
      │
      ▼
┌─────────────┐
│  Aggregate  │  Ward-level summaries                     [PHASE 1: SCAFFOLD]
└─────────────┘
      │
      ▼
┌─────────────┐
│   Alerts    │  Generate warnings                        [PHASE 1: SCAFFOLD]
└─────────────┘
      │
      ▼
   Storage
```

## Temporal Distinctions

- **Forecast Run Time**: When the model was initialized
- **Valid Time**: When the forecast applies to
- **Lead Time**: Difference between run time and valid time
- **Observation Time**: When the measurement was taken

## Implementation Status

### Phase 1 - IMPLEMENTED
- Data pipeline scaffolding (ingest, validate, normalize, spatialize)
- Database schema with all tables
- Alembic migration system
- API endpoints (scaffold)
- Worker task definitions (scaffold)
- Frontend pages (scaffold)

### Phase 2 - PLANNED
- UTCI/thermal comfort calculation
- Hazard index calculation
- Vulnerability scoring
- Exposure scoring
- HSRI calculation
- Risk classification
- Alert generation algorithms
