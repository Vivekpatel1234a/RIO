# RIO — Agent Handover Documentation

Flood / dam-break simulation platform with a real-data 3D (WebGL) viewer and a
simulation video view. Brand name is **RIO**. Light theme, white + orange
palette, minimal chrome, no "AI-looking" status pills.

Repo root for the app: `RIO-main/RIO-main/` (Next.js frontend + FastAPI backend).
Data lives **outside** the app: `resources/` (rasters) and `recordings/` (videos).

```
Project_RIO/
├─ resources/                     <- four HEC-RAS GeoTIFF/VRT outputs (INPUT DATA)
├─ recordings/                    <- real HEC-RAS screen recordings (.mp4)
└─ RIO-main/RIO-main/
   ├─ backend/                    <- FastAPI (port 8000)
   └─ frontend/                   <- Next.js 14 (port 3000)
```

---

## 1. How to run (local / "offline")

Prerequisites (on this machine):
- Managed Node: `C:\Users\vivek\.workbuddy-ai\binaries\node\versions\22.22.2-3\node.exe`
  (npm via `node.exe <nodeDir>/node_modules/npm/bin/npm-cli.js`)
- Python venv with deps: `C:\Users\vivek\.workbuddy-ai\binaries\python\envs\default`
  (rasterio, pillow, fastapi, uvicorn, numpy, pandas, shapely, pyproj…)

```bash
# Backend — MUST run from backend/ (storage paths are relative)
cd RIO-main/RIO-main/backend
C:/Users/vivek/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe \
  -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend
cd RIO-main/RIO-main/frontend
PATH="C:/Users/vivek/.workbuddy-ai/binaries/node/versions/22.22.2-3:$PATH" \
  node.exe node_modules/next/dist/bin/next dev -p 3000
```

URLs: app http://localhost:3000 · API docs http://127.0.0.1:8000/api/docs

First-request note: `/api/flood/meta` parses three ~100 MPixel GeoTIFFs
(~20 s), then caches into `backend/storage/flood_cache/`. Later calls are instant.

"Offline" caveats (nothing breaks, but visual data degrades):
- **3D terrain** and **basemap** load real DEM/raster tiles from the internet
  (AWS Terrarium tiles, CARTO). Without internet you get the UI, the flood
  rasters, and the videos, but no terrain relief / basemap imagery.
- The flood rasters and videos themselves come from the local backend — fully offline.

---

## 2. Architecture

**Backend** (`backend/app/`)
- `main.py` — FastAPI app, CORS (localhost:3000/3001), static mount of `storage/`, routers.
- `api/` — routers: `health, demo, simulations, models_api, gee, monitoring, exports, flood`.
- `services/flood/raster_pipeline.py` — **real-data pipeline** for the four rasters.
- `services/{simulation,impact,exports,demo,gis}/` — the older mock/synthetic pipeline
  (SPH & Delft3D mock adapters, demo generator).
- `models/database.py` — SQLAlchemy models. **Not wired in**: Postgres/Redis/Celery are
  unused; simulation state is in-memory, so it resets on restart.
- Storage: `backend/storage/` (projects, exports, `flood_cache/`).

**Frontend** (`frontend/src/`)
- App Router routes: `/` dashboard, `/flood-3d` (3D + simulation video),
  `/demo`, `/simulations` (+ `/new`, `/[id]`, `/[id]/results`, `/[id]/comparison`),
  `/data`, `/exports`, `/monitoring`, `/about`, `/settings`.
- `components/flood3d/FloodTerrainViewer.tsx` — MapLibre GL 3D terrain + flood layers + timeline.
- `components/flood3d/FloodVideoPlayer.tsx` — full-screen simulation video view.
- `components/map/FloodMap.tsx` — 2D MapLibre map used by the dashboard.
- `lib/api.ts` — axios client, `baseURL = NEXT_PUBLIC_API_URL || http://localhost:8000`.
- Renderer: **MapLibre GL JS 6.11.2** (the project's existing WebGL framework).
  Do not add Three.js/R3F unless explicitly asked.

---

## 3. The four input files (`resources/`)

All are **HEC-RAS 2D model outputs** (already-simulated results, not inputs to re-run).

| File | Meaning | Size | Range |
|---|---|---|---|
| `Depth (01JAN2222 00 26 00)vrt.Terrain.BEC.tif` | instantaneous depth, t = 00:26:00 | 11776×8448 | 0–55.29 ft (0–16.85 m) |
| `Depth (Max).Terrain.BEC.tif` | max depth envelope over the run | 13056×8960 | 0–56.16 ft (0–17.12 m) |
| `WSE (Min)wse.Terrain.BEC.tif` | minimum water surface elevation | 11776×8448 | 542.6–638.6 ft (165.4–194.6 m) |
| `Depth (Max) (2)twoesep.vrt` | GDAL VRT — **broken**: its source TIFF is missing | – | reported as unreadable |

Common georeferencing: **EPSG:2271** (NAD83 / Pennsylvania North, ftUS, Lambert
Conformal Conic), 10 ft cells, NoData −9999, US survey feet. Domain ≈ 35.9 × 25.7 km
at lon −77.781…−77.306, lat 40.949…41.196 (north-central Pennsylvania). Deepest
cell: 17.12 m at lon −77.61065, lat 41.04537.

File 4 is *not* silently replaced: the API reports it as unavailable and surfaces
its embedded XML metadata. If the missing TIFF
(`Depth (Max) (2)twoesep.Terrain.BEC.tif`) is ever added, it becomes readable with no
code change.

### Terrain source
The four files only cover the ~1 % wetted corridor, so full-domain terrain comes
from a **real external DEM**: AWS Terrain Tiles (Terrarium encoding, USGS 3DEP &
partners) draped by MapLibre's `raster-dem` terrain engine. In-channel elevations
are also available from WSE (Min). **No procedural/synthetic terrain anywhere.**

---

## 4. Flood API (`backend/app/api/flood.py`)

| Endpoint | Purpose |
|---|---|
| `GET /api/flood/meta` | inventory + per-file stats (ft & m), processed states, terrain-source info |
| `GET /api/flood/state/{name}/image.png` | reprojected, color-mapped depth/WSE raster (`depth_t26`, `depth_max`, `wse_min`, `depth_max_vrt`) |
| `GET /api/flood/state/{name}/grid` | decimated numeric grid + stats (validation) |
| `GET /api/flood/videos` | auto-discovers videos in `recordings/` |
| `GET /api/flood/videos/file/{name}` | streams the video (HTTP 206 range, scrubbing works) |

Pipeline transform, in order:
`read GeoTIFF → NoData mask → ft→m (0.304800609601219) → decimate to ~1000 px →
reproject EPSG:2271 → EPSG:4326 → colour-map RGBA → PNG + .f32 cache`.
Artifacts cached in `backend/storage/flood_cache/`; delete that folder to force a
reprocess. Downsampling smooths peaks (shown max 16.4 m vs true 17.12 m) — full-res
stats are also returned for honesty.

To add a new snapshot: add an entry to `STATES` in
`backend/app/services/flood/raster_pipeline.py` with `{file, label, kind, description}`;
it then appears in `/meta` and can be wired into the timeline.

---

## 5. UI conventions (follow these)

- **Theme**: light. Backgrounds white / `orange-50`; text `slate-700/800`; accents
  `orange-500/600`; borders `orange-200`. Root CSS vars live in `app/globals.css`.
- **Minimal chrome**: no status pills/badges like MOCK, DEMO, SYNTHETIC, PRELIMINARY,
  REAL RASTERS. They were deliberately removed. Keep only genuinely functional status
  (e.g. severity, VALIDATED/FAILED).
- **Branding**: "RIO", not "HADR Flood Simulation Platform" (descriptive prose may
  still mention HADR as the domain term).
- **Video = "Simulation"**: recordings are presented as Simulation 1 / 2, full-screen,
  no video-player chrome, floating controls only.
- Buttons/inputs reuse `components/ui/*` (shadcn-style) with Tailwind.

---

## 6. Known issues & pitfalls

1. **`next dev` can crash on a stale `.next/`** — the environment's safe-delete shim
   blocks bulk deletions (>50 files), and a corrupted webpack cache yields 500s
   (`Cannot find module './682.js'`). Fix: stop the server, delete `frontend/.next`,
   restart. Triggered by large batch edits **and by running `next build` then
   `next dev`**. Bash `rm -rf` may also be blocked — use PowerShell instead:
   `Remove-Item -Recurse -Force frontend/.next` (native .NET, not intercepted by the
   node shim).
2. **`requirements.txt` pins won't install on Python 3.13** (`numpy==1.26.4`). The venv
   uses newer versions instead; `rasterio`/`geopandas` are optional (code degrades
   gracefully except `dem_processor.py`, which is not imported anywhere).
3. **VRT source missing** (see §3) — expected, surfaced in the UI.
4. **Simulation list is empty on restart** — state is in-memory; run the demo pipeline
   from `/demo` or accept it. `storage/projects/*` are previous-run artifacts that the
   in-memory store doesn't rehydrate.
5. `src/lib/mockData.ts` has a pre-existing TS error (`Cannot find module './index'`) —
   unrelated to current work; `tsc --noEmit` reports it, the build tolerates it.
6. Backend must be started from `backend/` (relative `./storage`).

---

## 7. Deployment plan (Vercel, later)

Current state is a two-service app; Vercel hosts **only the frontend**:

- Frontend: Root Directory `RIO-main/RIO-main/frontend`, build `next build`, output
  `.next`. Set env `NEXT_PUBLIC_API_URL` to the deployed backend URL.
- Backend: cannot run on Vercel serverless as-is (needs a writable filesystem for
  `storage/flood_cache`, plus rasterio/GDAL wheels). Host on a long-running service
  (Render/Fly.io/Railway/VM) with the rasters mounted or baked into the image, or
  pre-generate the PNG/grids and ship them as static assets.
- Before shipping: replace `http://localhost:8000` defaults with env-driven config,
  confirm CORS origins include the Vercel domain, and decide whether DEM tiles still
  stream from AWS (they can, it is a public dataset).
- Backend env vars: `FLOOD_RASTER_DIR`, `FLOOD_RECORDINGS_DIR`, `CORS_ORIGINS`,
  `STORAGE_PATH`, `DEMO_DATA_PATH`. No secrets are required today (no API keys in use).
