# Data Flow

## Weather Pipeline

```
External Source
      │
      ▼
┌─────────────┐
│   Ingest    │  Fetch forecast/observation data
└─────────────┘
      │
      ▼
┌─────────────┐
│  Validate   │  Check data quality
└─────────────┘
      │
      ▼
┌─────────────┐
│  Normalize  │  Convert to standard units
└─────────────┘
      │
      ▼
┌─────────────┐
│ Spatialize  │  Assign to grid cells
└─────────────┘
      │
      ▼
┌─────────────┐
│  UTCI Calc  │  Calculate thermal comfort
└─────────────┘
      │
      ▼
┌─────────────┐
│   Hazard    │  Normalize to hazard index
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
│  HSRI Calc  │  H × V × E
└─────────────┘
      │
      ▼
┌─────────────┐
│  Classify   │  LOW | MEDIUM | HIGH
└─────────────┘
      │
      ▼
┌─────────────┐
│  Aggregate  │  Ward-level summaries
└─────────────┘
      │
      ▼
┌─────────────┐
│   Alerts    │  Generate warnings
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
