# Evaluation Service

A lightweight Django REST Framework microservice for evaluating feature flags. SDK clients send context (user_key, attributes) along with flag_key, project_id, and environment_key, and this service evaluates and returns the flag value by calling the flag_service via HTTP.

## Features

- Single and bulk flag evaluation
- User-keyed rollout percentage hashing
- Evaluation logging with filtering
- Health check endpoint
- Calls flag_service for flag configuration

## Requirements

- Python 3.11+
- PostgreSQL 15+
- flag_service running on port 8002

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver 8003
```

### Docker

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/evaluate/` | Evaluate a single flag |
| POST | `/api/v1/evaluate/bulk/` | Evaluate multiple flags |
| GET | `/api/v1/logs/` | List evaluation logs |
| GET | `/health/` | Health check |

## API Usage

### Evaluate a Single Flag

```http
POST /api/v1/evaluate/
Content-Type: application/json

{
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "environment_key": "production",
    "flag_key": "new-checkout-flow",
    "user_key": "user-123",
    "attributes": {
        "plan": "premium",
        "country": "US"
    }
}
```

**Response:**
```json
{
    "flag_key": "new-checkout-flow",
    "value": true,
    "reason": "DEFAULT",
    "evaluated_at": "2024-01-15T10:30:00Z"
}
```

### Evaluate Multiple Flags (Bulk)

```http
POST /api/v1/evaluate/bulk/
Content-Type: application/json

{
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "environment_key": "production",
    "user_key": "user-123",
    "flag_keys": ["feature-a", "feature-b", "feature-c"],
    "attributes": {
        "plan": "premium"
    }
}
```

**Response:**
```json
[
    {"flag_key": "feature-a", "value": true, "reason": "DEFAULT", "evaluated_at": "..."},
    {"flag_key": "feature-b", "value": false, "reason": "ROLLOUT_EXCLUDED", "evaluated_at": "..."},
    {"flag_key": "feature-c", "value": null, "reason": "FLAG_NOT_FOUND", "evaluated_at": "..."}
]
```

### List Evaluation Logs

```http
GET /api/v1/logs/?project_id=550e8400-e29b-41d4-a716-446655440000&flag_key=new-checkout-flow
```

## Evaluation Reasons

| Reason | Description |
|--------|-------------|
| `DEFAULT` | Flag is enabled, user receives the default/control value |
| `DISABLED` | Flag is not enabled |
| `ROLLOUT_EXCLUDED` | User is excluded by rollout percentage |
| `FLAG_NOT_FOUND` | Flag does not exist in flag_service |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | - | Django secret key (required in production) |
| `DEBUG` | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | `localhost` | Comma-separated allowed hosts |
| `DB_NAME` | `evaluation_service_db` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL username |
| `DB_PASSWORD` | - | PostgreSQL password |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `CORS_ALLOW_ALL_ORIGINS` | `False` | Allow all CORS origins (dev only) |
| `FLAG_SERVICE_URL` | `http://localhost:8002` | URL of the flag_service |

## Running Tests

```bash
python manage.py test apps.evaluation.tests
```

## Service Port

This service runs on **port 8003**.
