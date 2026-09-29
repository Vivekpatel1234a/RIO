# RIO

Flood / dam-break simulation platform. Visualizes **real** HEC-RAS 2D model
outputs as an interactive 3D WebGL scene (real DEM terrain + real flood rasters)
and as a full-screen simulation playback of the recorded model runs.

- Frontend: Next.js 14 + MapLibre GL (WebGL), light theme
- Backend: FastAPI + rasterio (parses the real GeoTIFF outputs)
- Data: HEC-RAS rasters in `resources/`, run recordings in `recordings/`

## Quick start (local)

```bash
# Backend — run from the backend folder (storage paths are relative)
cd RIO-main/RIO-main/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend
cd RIO-main/RIO-main/frontend
npm install && npm run dev -p 3000
```

App: http://localhost:3000 · API docs: http://127.0.0.1:8000/api/docs
3D + simulation view: http://localhost:3000/flood-3d

Python deps: `fastapi uvicorn[standard] pydantic-settings sqlalchemy numpy pandas
scipy shapely pyproj python-multipart aiofiles httpx python-dotenv loguru rasterio pillow`

## Deploying the frontend (Vercel)

- Import this repo, set **Root Directory** to `RIO-main/RIO-main/frontend`
- Framework preset: Next.js (build `next build`, output `.next`)
- Env var: `NEXT_PUBLIC_API_URL` → URL of the deployed backend

The backend is **not** Vercel-serverless compatible as-is (needs a writable
filesystem for its raster cache and GDAL/rasterio wheels) — host it on a
long-running service (Render / Fly.io / Railway / a VM).

Hosting the backend on **PythonAnywhere**: see
[`DEPLOY-PYTHONANYWHERE.md`](DEPLOY-PYTHONANYWHERE.md) (step-by-step, plus the
exact Vercel env vars that wire the two together).

**Free backend hosting (recommended)**: [`DEPLOY-FREE.md`](DEPLOY-FREE.md) —
Koyeb free (always-on Docker container, no cold start), Render free as fallback,
plus the Vercel env vars. Same `backend/Dockerfile` works on both.

## Data notes

- Rasters in `resources/` are EPSG:2271 (US survey feet), reprojected to
  EPSG:4326 and converted to metres by the backend.
- `recordings/` is excluded from git (large media). To publish it, use Git LFS.
- Full agent handover docs: [`RIO-main/RIO-main/AGENTS.md`](RIO-main/RIO-main/AGENTS.md)
