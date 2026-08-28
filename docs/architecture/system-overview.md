# System Overview

## Architecture

The Heatwave Early Warning Platform is a modular, scalable system designed to convert meteorological forecasts and population vulnerability data into spatially and temporally resolved Human Thermal Stress Risk Index (HSRI) values.

### Core Formula

```
HSRI = H x V x E
```

Where:
- **H** = UTCI-derived Hazard Index (0.0 - 1.0) [PHASE 2]
- **V** = BBWM-derived Vulnerability Index (0.0 - 1.0) [PHASE 2]
- **E** = BBWM-derived Exposure Index (0.0 - 1.0) [PHASE 2]

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
State → City → Ward ←→ Grid Cell (~333m)
              ↑           ↓
              └── GridWardIntersection ──┘
```

The `grid_ward_intersections` table supports accurate ward aggregation when grid cells cross administrative boundaries.

### Data Flow

1. **Weather Ingestion**: External forecast/observation data [PHASE 1: SCAFFOLD]
2. **Quality Control**: Validation and normalization [PHASE 1: SCAFFOLD]
3. **Spatialization**: Assignment to grid cells [PHASE 1: SCAFFOLD]
4. **UTCI Calculation**: Thermal comfort index [PHASE 2: PLANNED]
5. **Hazard Assessment**: Normalized hazard index [PHASE 2: PLANNED]
6. **Vulnerability Assessment**: Population vulnerability [PHASE 2: PLANNED]
7. **Exposure Assessment**: Population exposure [PHASE 2: PLANNED]
8. **Risk Calculation**: HSRI = H x V x E [PHASE 2: PLANNED]
9. **Aggregation**: Ward-level summaries [PHASE 1: SCAFFOLD]
10. **Alert Generation**: Warnings and recommendations [PHASE 1: SCAFFOLD]

## Implementation Status

### Phase 1 - IMPLEMENTED
- Repository architecture
- Backend foundation (FastAPI)
- Frontend foundation (Next.js)
- PostgreSQL + PostGIS + TimescaleDB configuration
- Redis/Celery worker foundation
- Database schema (22 tables)
- Alembic migration system
- Spatial data architecture (grid_ward_intersections)
- Weather time-series architecture (hypertables)
- Scientific module interfaces (abstract base classes)
- Scientific configuration management (YAML files)
- API contracts (scaffold)
- Pipeline contracts (scaffold)
- Testing infrastructure
- Docker development environment
- Basic Kubernetes/monitoring scaffolding
- Documentation

### Phase 2 - PLANNED
- UTCI/thermal comfort calculation
- Hazard index calculation
- Vulnerability scoring (BBWM)
- Exposure scoring (BBWM)
- HSRI calculation (H x V x E)
- Risk classification
- Alert generation algorithms
- Real weather-provider integration
- Full GIS analytics

### Later Phases - PLANNED
- Historical Health Dataset
- Mortality/Hospitalization ML
- 3-5 Day Health Impact Prediction
- SMS/WhatsApp integration
- Production alert algorithms
