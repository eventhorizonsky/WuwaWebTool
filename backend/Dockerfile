# Build from project root:  docker build -f backend/Dockerfile -t wuwawebtool .
# ─── Stage 1: Frontend build ───
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Python backend ───
FROM python:3.12-slim

WORKDIR /app/backend

# Install system dependencies (Debian Bookworm package names)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0t64 libsm6 libxext6 libxrender1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Data directory for CDN-downloaded resources
RUN mkdir -p /app/backend/data/XutheringWavesUID

ENV WUWA_DATA_PATH=/app/backend/data
ENV PORT=8000

EXPOSE ${PORT:-8000}

# Shell form so $PORT is expanded (Railway / Render inject this automatically)
CMD uvicorn main:app --host :: --port ${PORT:-8000} --forwarded-allow-ips '*'
