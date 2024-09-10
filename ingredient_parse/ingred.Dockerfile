FROM python:3.11

WORKDIR /app

# Install Python dependencies
COPY ingred-requirements.txt .
RUN pip install --no-cache-dir -r ingred-requirements.txt