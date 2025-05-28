# Use official Python slim image
FROM python:3.11-slim

# Prevent Python from writing pyc files to disk and buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system deps (if any; e.g. for cryptography)
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libffi-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Entrypoint: run the aiogram bot
CMD ["python", "main.py"]
