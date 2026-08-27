# Incident Response

## Overview

This document outlines procedures for responding to incidents in the Heatwave Early Warning Platform.

## Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| P1 | Complete system outage | Immediate |
| P2 | Major feature unavailable | 1 hour |
| P3 | Minor feature degraded | 4 hours |
| P4 | Cosmetic issue | 24 hours |

## Common Incidents

### API Unavailable

1. Check API logs: `docker logs heatwave_api`
2. Verify database connectivity
3. Check Redis connectivity
4. Restart API if needed: `docker restart heatwave_api`

### Worker Not Processing

1. Check worker logs: `docker logs heatwave_worker`
2. Verify Redis queue: `redis-cli llen celery`
3. Restart worker: `docker restart heatwave_worker`

### Database Issues

1. Check PostgreSQL logs: `docker logs heatwave_db`
2. Verify connections: `pg_isready -h localhost -p 5432`
3. Check disk space
4. Restart database: `docker restart heatwave_db`

### High Memory Usage

1. Identify container: `docker stats`
2. Check for memory leaks in logs
3. Restart affected container
4. Scale if needed: `docker-compose up -d --scale worker=3`

## Escalation

1. Try basic troubleshooting (restart, check logs)
2. Check monitoring dashboards
3. Contact on-call engineer
4. Document incident in post-mortem

## Post-Incident

1. Create incident report
2. Identify root cause
3. Implement preventive measures
4. Update runbooks if needed
