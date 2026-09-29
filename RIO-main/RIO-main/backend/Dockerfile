# Build context: repository ROOT.
#   Koyeb / Render / Railway: Dockerfile path = RIO-main/RIO-main/backend/Dockerfile,
#   build context = repo root (leave "root directory" empty).
FROM python:3.11-slim

WORKDIR /app

# No apt/gdal step needed: rasterio's manylinux wheel bundles GDAL. Dropping
# libgdal-dev keeps the image ~250 MB smaller and the build several minutes
# faster — which matters a lot on free tiers (0.1 vCPU).
# If a future rasterio version has no wheel for your Python, re-add:
#   RUN apt-get update && apt-get install -y libgdal-dev gcc g++ \
#       && rm -rf /var/lib/apt/lists/*

# Python deps
COPY RIO-main/RIO-main/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend source
COPY RIO-main/RIO-main/backend/ ./

# Real HEC-RAS rasters (auto-discovered at /app/resources by the flood pipeline)
COPY resources ./resources

# Recordings are gitignored. To ship the videos, commit them with Git LFS
# (`git lfs track "recordings/*.mp4"`) and uncomment the next line.
# COPY recordings ./recordings

RUN mkdir -p /app/storage /app/demo /app/storage/flood_cache

# Container-side paths. Every one of these can be overridden by an env var
# in the hosting dashboard.
ENV STORAGE_PATH=/app/storage \
    DEMO_DATA_PATH=/app/demo \
    FLOOD_RASTER_DIR=/app/resources \
    FLOOD_RECORDINGS_DIR=/app/recordings \
    APP_ENV=production \
    DEBUG=false \
    CORS_ORIGIN_REGEX="https://.*\.vercel\.app"

# Bake the raster cache into the IMAGE. Reprojecting the ~100M-cell HEC-RAS
# rasters takes tens of seconds on a 0.1 vCPU free instance, so doing it here
# (once, at build time) means the first request after a cold start is instant.
RUN python precompute_flood.py || echo "precompute skipped — rasters unavailable"

EXPOSE 8000

# Shell form so ${PORT} is expanded at runtime (Koyeb/Render/Railway inject PORT)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
