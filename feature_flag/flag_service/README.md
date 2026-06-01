# flag_service

Feature Flag microservice for a Feature Flag SaaS platform. Manages Flags, Variations, Segments, and Targeting Rules.

## Overview

- **Port**: 8002
- **Database**: PostgreSQL (`flag_service_db`)
- **Framework**: Django 4.2 + Django REST Framework 3.14
- **Settings module**: `flag_service.settings.local` (development), `flag_service.settings.production` (production)

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- PostgreSQL 15+

### Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your local values

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8002
```

### Docker (Recommended)

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up --build -d
```

## API Endpoints

| Method | Endpoint                        | Description                  |
|--------|---------------------------------|------------------------------|
| GET    | /api/v1/flags/                  | List all flags               |
| POST   | /api/v1/flags/                  | Create a new flag            |
| GET    | /api/v1/flags/{id}/             | Retrieve a flag              |
| PUT    | /api/v1/flags/{id}/             | Full update a flag           |
| PATCH  | /api/v1/flags/{id}/             | Partial update a flag        |
| DELETE | /api/v1/flags/{id}/             | Delete a flag                |
| POST   | /api/v1/flags/{id}/toggle/      | Toggle flag is_enabled       |
| GET    | /api/v1/variations/             | List all variations          |
| POST   | /api/v1/variations/             | Create a variation           |
| GET    | /api/v1/variations/{id}/        | Retrieve a variation         |
| PUT    | /api/v1/variations/{id}/        | Update a variation           |
| DELETE | /api/v1/variations/{id}/        | Delete a variation           |
| GET    | /api/v1/targeting-rules/        | List all targeting rules     |
| POST   | /api/v1/targeting-rules/        | Create a targeting rule      |
| GET    | /api/v1/targeting-rules/{id}/   | Retrieve a targeting rule    |
| PUT    | /api/v1/targeting-rules/{id}/   | Update a targeting rule      |
| DELETE | /api/v1/targeting-rules/{id}/   | Delete a targeting rule      |
| GET    | /api/v1/segments/               | List all segments            |
| POST   | /api/v1/segments/               | Create a segment             |
| GET    | /api/v1/segments/{id}/          | Retrieve a segment           |
| PUT    | /api/v1/segments/{id}/          | Update a segment             |
| DELETE | /api/v1/segments/{id}/          | Delete a segment             |
| GET    | /health/                        | Health check                 |

## Filtering

### Flags

- `?project_id=<uuid>`
- `?environment_key=<string>`
- `?is_enabled=true|false`
- `?flag_type=boolean|string|number|json`

### Segments

- `?project_id=<uuid>`

## Pagination

All list endpoints support pagination:

- `?page=<int>` — page number (default: 1)
- `?page_size=<int>` — items per page (default: 20, max: 100)

## Running Tests

```bash
python manage.py test apps.flags.tests apps.segments.tests
```

## Admin

Access Django admin at `/admin/` after creating a superuser.

## Environment Variables

| Variable               | Description                        | Default                                     |
|------------------------|------------------------------------|---------------------------------------------|
| `SECRET_KEY`           | Django secret key                  | (required)                                  |
| `DEBUG`                | Debug mode                         | `False`                                     |
| `ALLOWED_HOSTS`        | Comma-separated allowed hosts      | `localhost,127.0.0.1`                       |
| `DB_NAME`              | PostgreSQL database name           | `flag_service_db`                           |
| `DB_USER`              | PostgreSQL user                    | `postgres`                                  |
| `DB_PASSWORD`          | PostgreSQL password                | (required)                                  |
| `DB_HOST`              | PostgreSQL host                    | `localhost`                                 |
| `DB_PORT`              | PostgreSQL port                    | `5432`                                      |
| `CORS_ALLOW_ALL_ORIGINS` | Allow all CORS origins           | `False`                                     |
