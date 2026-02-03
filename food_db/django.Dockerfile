FROM python:3.11-slim

WORKDIR /app

# Copy the application code
COPY . .

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies
RUN uv pip install --no-cache-dir --system -r django-requirements.txt

# Set Python path for easier imports
ENV PYTHONPATH=/app/food_db_app:/app

# When using cloud sync, you need this to access the Django database
ENV DJANGO_SETTINGS_MODULE=food_db.settings

# Run Django app
EXPOSE 8000
CMD python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    python manage.py migrate --database=test --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py runserver 0.0.0.0:8000