# System Overview

## Architecture

The Heatwave Early Warning Platform is a modular, scalable system designed to convert meteorological forecasts and population vulnerability data into spatially and temporally resolved Human Thermal Stress Risk Index (HSRI) values.

### Core Formula

```
HSRI = H × V × E
```

Where:
- **H** = UTCI-derived Hazard Index (0.0 - 1.0)
- **V** = BBWM-derived Vulnerability Index (0.0 - 1.0)
- **E** = BBWM-derived Exposure Index (0.0 - 1.0)

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                     │
│   Dashboard | Risk Map | Wards | Forecasts | Alerts | Models│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│   /api/v1/health | /forecasts | /hazards | /risk | /alerts  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Scientific Engine                          │
│   Thermal Comfort | Hazard | Vulnerability | Exposure | Risk│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                │
│   PostgreSQL + PostGIS + TimescaleDB | Redis                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Background Workers (Celery)                  │
│   Weather Pipeline | Risk Pipeline | Alert Generation       │
└─────────────────────────────────────────────────────────────┘
```

### Spatial Hierarchy

```
State → City → Ward → Grid Cell (~333m)
```

### Data Flow

1. **Weather Ingestion**: External forecast/observation data
2. **Quality Control**: Validation and normalization
3. **Spatialization**: Assignment to grid cells
4. **UTCI Calculation**: Thermal comfort index
5. **Hazard Assessment**: Normalized hazard index
6. **Vulnerability Assessment**: Population vulnerability
7. **Exposure Assessment**: Population exposure
8. **Risk Calculation**: HSRI = H × V × E
9. **Aggregation**: Ward-level summaries
10. **Alert Generation**: Warnings and recommendations
