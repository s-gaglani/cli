FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=evaluation_service.settings.local

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput --settings=evaluation_service.settings.local 2>/dev/null || true

# Expose port
EXPOSE 8003

# Run the application
CMD ["gunicorn", "evaluation_service.wsgi:application", "--bind", "0.0.0.0:8003", "--workers", "4", "--timeout", "120"]
