# Heatwave Early Warning Platform

Extreme Heatwave Early Warning and Human Thermal Stress Index Platform for the Indian Ministry of Earth Sciences.

## Project Structure

```
heatwave-platform/
├── apps/
│   ├── api/           # FastAPI backend
│   ├── worker/        # Background workers
│   └── web/           # Next.js frontend
├── scientific/        # Scientific modules
│   ├── core/          # Base classes
│   ├── hazard/        # Hazard calculation
│   ├── vulnerability/ # Vulnerability calculation
│   ├── exposure/      # Exposure calculation
│   ├── risk/          # Risk calculation
│   ├── thermal_comfort/ # Thermal comfort models
│   └── configuration/ # Scientific configuration
├── pipelines/         # Data pipelines
├── db/               # Database migrations
├── infra/            # Infrastructure
├── tests/            # Test suites
└── docs/             # Documentation
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+

### Development Setup

1. Start infrastructure:
```bash
docker-compose up -d
```

2. Install API dependencies:
```bash
cd apps/api
pip install -r requirements.txt
```

3. Install web dependencies:
```bash
cd apps/web
npm install
```

4. Run the API:
```bash
cd apps/api
uvicorn app.main:app --reload
```

5. Run the frontend:
```bash
cd apps/web
npm run dev
```

### Access Services
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Scientific Model

The platform implements the Human Thermal Stress Risk Index (HSRI):

```
HSRI = H × V × E
```

Where:
- H = UTCI-derived Hazard Index
- V = BBWM-derived Vulnerability Index
- E = BBWM-derived Exposure Index

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scientific tests/

# Run specific test
pytest tests/test_utci.py -v
```

## License

Government of India - Ministry of Earth Sciences
