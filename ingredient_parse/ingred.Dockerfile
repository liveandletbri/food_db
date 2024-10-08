FROM python:3.11

WORKDIR /app

# Install Python dependencies
COPY ingred-requirements.txt .
RUN pip install --no-cache-dir -r ingred-requirements.txt

# Copy the application code
COPY parse_api parse_api

EXPOSE 5000
CMD python parse_api/api.py