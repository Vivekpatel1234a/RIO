# Build context: repository ROOT (Railway: set Dockerfile path to
# RIO-main/RIO-main/backend/Dockerfile and leave Root Directory empty).
FROM python:3.11-slim

WORKDIR /app

# GDAL / build tooling (rasterio, psycopg2)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Python deps
COPY RIO-main/RIO-main/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend source
COPY RIO-main/RIO-main/backend/ ./

# Real HEC-RAS rasters (auto-discovered at /app/resources by the flood pipeline)
COPY resources ./resources

# Recordings are gitignored — uncomment once the videos are committed
# COPY recordings ./recordings

RUN mkdir -p /app/storage /app/demo

EXPOSE 8000

# Shell form so ${PORT} is expanded at runtime (Railway injects PORT)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
