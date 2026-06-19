# Build from project root:  docker build -f backend/Dockerfile -t wuwawebtool .
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

# Copy frontend static files (served by FastAPI StaticFiles)
COPY frontend/ /app/frontend

# Data directory for CDN-downloaded resources
RUN mkdir -p /app/backend/data/XutheringWavesUID

ENV WUWA_DATA_PATH=/app/backend/data
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
