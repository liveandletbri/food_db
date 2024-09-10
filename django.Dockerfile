FROM python:3.11-slim

WORKDIR /app

# Copy the application code
COPY food_db .

# Install Python dependencies
RUN pip install --no-cache-dir -r django-requirements.txt

# Run Django app
EXPOSE 8000
CMD python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py runserver 0.0.0.0:8000