FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# ── Bake in trained ML models ──────────────────
# .pkl files are copied directly into the image
# so the app works immediately without retraining
COPY backend/training/models/ ./backend/training/models/

# Create runtime directories
RUN mkdir -p /tmp/uploads /tmp/logs

# Set environment path overrides for Azure
ENV UPLOAD_DIR=/tmp/uploads
ENV LOG_DIR=/tmp/logs
ENV MODEL_DIR=/app/backend/training/models

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]