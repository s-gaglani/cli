# Project Service

Manages Organizations, Projects, Environments, and API Keys for the Feature Flag SaaS platform.

## Port: 8001

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver 8001
```

### Docker (Development)

```bash
docker-compose up --build
```

### Docker (Production)

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /health/` | Health check |
| `GET /api/v1/organizations/` | List organizations |
| `POST /api/v1/organizations/` | Create organization |
| `GET /api/v1/organizations/{id}/` | Retrieve organization |
| `PUT /api/v1/organizations/{id}/` | Update organization |
| `DELETE /api/v1/organizations/{id}/` | Delete organization |
| `GET /api/v1/api-keys/` | List API keys |
| `POST /api/v1/api-keys/` | Create API key |
| `GET /api/v1/projects/` | List projects |
| `POST /api/v1/projects/` | Create project |
| `GET /api/v1/environments/` | List environments |
| `POST /api/v1/environments/` | Create environment |

## Settings

- `project_service.settings.local` — local development (DEBUG=True)
- `project_service.settings.production` — production (DEBUG=False, strict)

## Running Tests

```bash
python manage.py test apps.organizations apps.environments
```
