# Heatwave Early Warning Platform

Extreme Heatwave Early Warning and Human Thermal Stress Index Platform for the Indian Ministry of Earth Sciences.

## Overview

This platform converts meteorological forecasts and population vulnerability data into spatially and temporally resolved Human Thermal Stress Risk Index (HSRI) values.

### Core Formula

```
HSRI = H × V × E
```

Where:
- **H** = UTCI-derived Hazard Index
- **V** = BBWM-derived Vulnerability Index
- **E** = BBWM-derived Exposure Index

## Project Structure

```
heatwave-platform/
├── apps/
│   ├── api/           # FastAPI backend
│   ├── worker/        # Celery background workers
│   └── web/           # Next.js frontend
├── scientific/        # Scientific modules
│   ├── core/          # Base classes
│   ├── hazard/        # Hazard calculation
│   ├── vulnerability/ # Vulnerability calculation
│   ├── exposure/      # Exposure calculation
│   ├── risk/          # Risk calculation
│   ├── thermal_comfort/ # Thermal comfort models
│   └── configuration/ # Scientific configuration YAMLs
├── pipelines/         # Data pipelines
├── db/               # Database migrations and SQL
├── infra/            # Infrastructure (Docker, K8s, monitoring)
├── tests/            # Test suites
└── docs/             # Documentation
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+

### Development Setup

1. **Start infrastructure:**
```bash
docker-compose up -d
```

2. **Install API dependencies:**
```bash
cd apps/api
pip install -r requirements.txt
```

3. **Install worker dependencies:**
```bash
cd apps/worker
pip install -r requirements.txt
```

4. **Install frontend dependencies:**
```bash
cd apps/web
npm install
```

5. **Run database migrations:**
```bash
cd apps/api
alembic upgrade head
```

6. **Start the API:**
```bash
uvicorn app.main:app --reload
```

7. **Start the worker:**
```bash
celery -A worker.main worker --loglevel=info
```

8. **Start the frontend:**
```bash
npm run dev
```

### Access Services
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Testing

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=scientific tests/

# Run specific test
pytest tests/test_scientific_interfaces.py -v
```

## Linting

```bash
# Run Python linting
cd apps/api
ruff check .

# Run frontend linting
cd apps/web
npm run lint
```

## Type Checking

```bash
# Run Python type checking
cd apps/api
mypy app/

# Run frontend type checking
cd apps/web
npm run type-check
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| GET /api/v1/health | Health check |
| GET /api/v1/forecasts | Weather forecasts |
| GET /api/v1/hazards | Hazard assessments |
| GET /api/v1/vulnerability | Vulnerability profiles |
| GET /api/v1/exposure | Exposure profiles |
| GET /api/v1/risk | Risk assessments |
| GET /api/v1/wards | Ward data |
| GET /api/v1/alerts | Active alerts |
| GET /api/v1/models | Scientific models |

## Scientific Models

| Model | Type | Description |
|-------|------|-------------|
| utci-v1 | Thermal Comfort | UTCI calculation |
| vulnerability-bbwm-v1 | Vulnerability | BBWM vulnerability scoring |
| exposure-bbwm-v1 | Exposure | BBWM exposure scoring |
| hsri-multiplicative-v1 | Risk | HSRI = H × V × E |

## Documentation

- [System Overview](docs/architecture/system-overview.md)
- [Data Flow](docs/architecture/data-flow.md)
- [Database Schema](docs/architecture/database.md)
- [Hazard Model](docs/scientific/hazard.md)
- [Vulnerability Model](docs/scientific/vulnerability.md)
- [Exposure Model](docs/scientific/exposure.md)
- [Risk Model](docs/scientific/risk.md)
- [Deployment Guide](docs/operations/deployment.md)
- [Monitoring Guide](docs/operations/monitoring.md)

## License

Government of India - Ministry of Earth Sciences
