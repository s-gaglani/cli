# Task Manager API

Production-grade Django REST Framework backend for task management.

## Quick Start

```bash
cp .env.example .env
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Docker

```bash
docker-compose up --build
```

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | /health/ | Health check |
| GET/POST | /api/v1/tasks/ | List / create tasks |
| GET/PUT/DELETE | /api/v1/tasks/{id}/ | Task detail |
| GET | /api/v1/users/ | List users (admin only) |

## Settings

| Env Var | Description |
|---------|-------------|
| SECRET_KEY | Django secret key |
| DEBUG | True/False |
| DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT | PostgreSQL |
| CORS_ALLOWED_ORIGINS | Comma-separated frontend origins |
