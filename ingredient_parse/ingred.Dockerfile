FROM python:3.11

WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies
COPY ingred-requirements.txt .
RUN uv pip install --no-cache-dir --system -r ingred-requirements.txt

# Copy the application code
COPY parse_api parse_api

EXPOSE 5000
CMD python parse_api/api.py