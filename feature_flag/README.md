# Feature Flag — Microservices Backend

Production-grade Django REST Framework backend for a Feature Flag SaaS platform.

## Architecture

Three independently deployable services communicate via REST APIs:

| Service | Port | Responsibility |
|---|---|---|
| `project_service` | 8001 | Organizations, Projects, Environments, API Keys |
| `flag_service` | 8002 | Feature Flags, Variations, Segments, Targeting Rules |
| `evaluation_service` | 8003 | SDK flag evaluation endpoint |

Each service has its own PostgreSQL database. Services reference each other by ID only — no shared database.

```
project_service (8001)         flag_service (8002)
  └── organizations               └── flags
  └── api_keys                    └── variations
  └── projects                    └── targeting_rules
  └── environments                └── segments

evaluation_service (8003)
  └── evaluation logs
  └── clients.py → calls flag_service
```

## Quick Start (all services)

```bash
# Copy env files (already populated for dev)
# Start everything
docker compose up --build

# Run migrations for each service
docker compose exec project_service python manage.py migrate
docker compose exec flag_service python manage.py migrate
docker compose exec evaluation_service python manage.py migrate
```

## Service Endpoints

### project_service — http://localhost:8001

```
GET/POST   /api/v1/organizations/
GET/PUT/DELETE /api/v1/organizations/{id}/
GET/POST   /api/v1/api-keys/
GET/POST   /api/v1/projects/
GET/PUT/DELETE /api/v1/projects/{id}/
GET/POST   /api/v1/environments/
GET        /health/
```

### flag_service — http://localhost:8002

```
GET/POST   /api/v1/flags/
GET/PUT/DELETE /api/v1/flags/{id}/
POST       /api/v1/flags/{id}/toggle/
GET/POST   /api/v1/variations/
GET/POST   /api/v1/targeting-rules/
GET/POST   /api/v1/segments/
GET        /health/
```

### evaluation_service — http://localhost:8003

```
POST       /api/v1/evaluate/
POST       /api/v1/evaluate/bulk/
GET        /api/v1/logs/
GET        /health/
```

## Evaluate a Flag

```bash
curl -X POST http://localhost:8003/api/v1/evaluate/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "<uuid>",
    "environment_key": "production",
    "flag_key": "dark-mode",
    "user_key": "user-123",
    "attributes": {"plan": "pro", "country": "US"}
  }'
```

Response:
```json
{
  "flag_key": "dark-mode",
  "value": true,
  "reason": "DEFAULT",
  "evaluated_at": "2026-01-01T00:00:00Z"
}
```

## Run Tests

```bash
# Per service
cd project_service && python manage.py test apps
cd flag_service && python manage.py test apps
cd evaluation_service && python manage.py test apps
```

## Local Development (without Docker)

```bash
# Each service independently
cd project_service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

Repeat for `flag_service` (port 8002) and `evaluation_service` (port 8003).

## Extension Points

- **Authentication**: Add JWT or API key auth in each service's `permissions.py`
- **Caching**: Add Redis to `evaluation_service` for hot-path flag lookups
- **Async evaluation**: Replace `requests` in `clients.py` with `httpx` for async support
- **Webhooks**: Add a `webhook_service` that consumes flag change events
- **Analytics**: Extend `EvaluationLog` for flag usage analytics

## Service Communication

`evaluation_service → flag_service` is the only inter-service call.  
Configure `FLAG_SERVICE_URL` in `evaluation_service/.env`.

All other cross-service references use UUIDs only (e.g., `project_id`, `segment_id`).
