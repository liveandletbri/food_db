FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY django-requirements.txt .
RUN pip install --no-cache-dir -r django-requirements.txt

# Copy the application code
COPY food_db .

# Run Django app
EXPOSE 8000
CMD python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py runserver 0.0.0.0:8000