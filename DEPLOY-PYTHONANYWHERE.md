# Deploying the RIO backend to PythonAnywhere + connecting Vercel

Everything below assumes:

- **Backend**: `RIO-main/RIO-main/backend` (FastAPI) → **PythonAnywhere**
- **Frontend**: `RIO-main/RIO-main/frontend` (Next.js 14) → **Vercel**

---

## 0. Read this first — what PythonAnywhere can and cannot do here

| Thing | Free "Beginner" | Developer ($10/mo) |
|---|---|---|
| Disk | **512 MB** | 5 GB |
| CPU | **100 s/day** | 5 000 s/day |
| Outbound internet from your code | whitelist only | unrestricted |
| Scheduled / always-on tasks | none | 20 scheduled / 1 always-on |
| Static file mappings | yes (Web tab) | yes |
| Bandwidth | low | medium |

Your app needs roughly: Python packages (numpy + rasterio with bundled GDAL ≈ 250–350 MB)
+ `resources/` rasters 14 MB + `recordings/` videos 93 MB + generated cache ~22 MB.

**That does not fit in 512 MB.** So either:

1. Buy the **Developer plan ($10/mo)** — recommended, or
2. Stay free and **skip the videos** (don't upload `recordings/`) and install only
   `numpy + rasterio + pillow + fastapi + a2wsgi` (the slim file already excludes
   pandas/scipy/celery/sqlalchemy, which nothing imports).

Two honest caveats:

- PythonAnywhere's native ASGI support is still **beta** (command-line only). The
  stable path is the classic **WSGI** web app with the `a2wsgi` adapter — that's what
  this guide uses. (See §6 for the ASGI/uvicorn variant if you prefer it.)
- If you already have a card and just want it live, **Render / Railway is far less
  work**: `backend/Dockerfile` + `railway.json` are already written and tested.
  PythonAnywhere is the choice when you specifically want it there.

---

## 1. Create the account

1. Sign up at <https://www.pythonanywhere.com/registration/register/beginner/>
   (or pick Developer at checkout). Note your **username** — your site will be
   `https://<username>.pythonanywhere.com`.
2. EU users get `<username>.eu.pythonanywhere.com` — use whichever the dashboard shows.

---

## 2. Get the code onto PythonAnywhere

Open a **Bash console** (Consoles → Bash) and run:

```bash
# GitHub is whitelisted even on free accounts, so cloning works.
git clone https://github.com/<you>/<repo>.git RIO
cd RIO
# If resources/ is not in your repo, upload it via the Files tab instead.
ls RIO-main/RIO-main/backend          # must contain app/, requirements-pythonanywhere.txt
ls resources                          # 3 .tif + 1 .vrt
```

The layout you need on disk (flatten it if your clone nests differently):

```
/home/<username>/RIO/
├── resources/        # the four HEC-RAS files   (from the repo)
├── recordings/       # the two .mp4 files       (git-ignored → upload by hand)
└── backend/          # = RIO-main/RIO-main/backend
    ├── app/
    ├── pythonanywhere_wsgi.py
    ├── precompute_flood.py
    └── requirements-pythonanywhere.txt
```

Upload `recordings/*.mp4` through the **Files** tab (or skip them — see §0).

> `resources/`, `recordings/` and `backend/` must be siblings, because
> `raster_pipeline` walks up from the backend looking for a `resources/` folder.

---

## 3. Create the virtualenv and install dependencies

Still in the Bash console:

```bash
mkvirtualenv rio-venv --python=python3.11      # 3.11 has rasterio manylinux wheels
pip install --upgrade pip
cd /home/$USER/RIO/backend
pip install -r requirements-pythonanywhere.txt
python -c "import rasterio, numpy, fastapi, a2wsgi; print(rasterio.__gdal_version__)"
```

If `rasterio` fails to build, you're on a Python version without a wheel — recreate
the venv with `--python=python3.10` or `3.11`. You do **not** need to install GDAL:
the rasterio wheel bundles it (PythonAnywhere gives you no `apt` anyway).

---

## 4. Pre-compute the raster cache (important — saves your CPU quota)

The first `/api/flood/meta` call otherwise scans the full-resolution rasters and
reprojects each state (≈3 s locally, but noticeably slower on a throttled cloud
CPU — and it reruns after every worker restart). Do it once in the console:

```bash
cd /home/$USER/RIO/backend
python precompute_flood.py
```

It writes `storage/flood_cache/*.png`, `*.f32`, `*.json` and `inventory.json`.
A web request now just reads those files. Re-run it whenever the rasters change.

---

## 5. Create the web app (WSGI + a2wsgi)

**Web** tab → **Add a new web app** → next → **Manual configuration** → Python 3.11
→ finish. Then set:

| Field | Value |
|---|---|
| Source code | `/home/<username>/RIO/backend` |
| Working directory | `/home/<username>/RIO/backend` |
| Virtualenv | `/home/<username>/.virtualenvs/rio-venv` |

Click the **WSGI configuration file** link and replace its contents with:

```python
import sys
sys.path.insert(0, '/home/<username>/RIO/backend')
from pythonanywhere_wsgi import application
```

Then edit `/home/<username>/RIO/backend/pythonanywhere_wsgi.py` and change the three
constants at the top:

```python
USERNAME        = "yourusername"
BASE            = "/home/yourusername/RIO"
FRONTEND_ORIGIN = "https://your-app.vercel.app"     # set in step 8
```

Back on the **Web** tab, add **Static files** entries (these bypass Python entirely):

| URL | Directory |
|---|---|
| `/storage/` | `/home/<username>/RIO/backend/storage` |
| `/api/flood/videos/file/` | `/home/<username>/RIO/recordings` |

(The second one makes the 93 MB videos free to serve. Skip it if you didn't upload them.)

Click **Reload**. Test:

```bash
curl https://<username>.pythonanywhere.com/api/health
curl https://<username>.pythonanywhere.com/api/flood/meta | head -c 400
```

Expected: `{"status":"healthy",...}` and a big JSON with `"raster_dir": ".../resources"`.

---

## 6. Alternative: native ASGI (uvicorn) instead of WSGI

Only if you want WebSockets later. It's **beta**: no Web tab entry, no static file
mappings, managed from the command line only.

```bash
pip install --upgrade pythonanywhere          # in the Bash console
pa website create --domain <username>.pythonanywhere.com \
  --command "/home/<username>/.virtualenvs/rio-venv/bin/uvicorn \
    --app-dir /home/<username>/RIO/backend --uds \${DOMAIN_SOCKET} app.main:app"
pa website reload --domain <username>.pythonanywhere.com
```

With this route you must export the env vars from §7 into the venv
(`~/.virtualenvs/rio-venv/bin/postactivate`) because there is no WSGI file to set them.

---

## 7. Backend environment variables

`pythonanywhere_wsgi.py` already sets these for you. If you'd rather use a
`.env` file (it must live in the working directory `/home/<username>/RIO/backend`):

```ini
APP_ENV=production
DEBUG=false
STORAGE_PATH=/home/<username>/RIO/backend/storage
DEMO_DATA_PATH=/home/<username>/RIO/backend/demo
FLOOD_RASTER_DIR=/home/<username>/RIO/resources
FLOOD_RECORDINGS_DIR=/home/<username>/RIO/recordings
CORS_ORIGINS=https://your-app.vercel.app
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
```

`CORS_ORIGIN_REGEX` is what makes Vercel **preview** deployments (`*.vercel.app`)
work without editing CORS after every push.

---

## 8. Vercel: point the frontend at the new backend

In your Vercel project → **Settings → Environment Variables**, add:

| Name | Value | Environments |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<username>.pythonanywhere.com` | Production + Preview |
| `BACKEND_URL` | `https://<username>.pythonanywhere.com` | Production + Preview |

(No trailing slash. `https`, not `http` — PythonAnywhere gives free SSL on
`*.pythonanywhere.com`, and Vercel is HTTPS-only, so `http` would be blocked as
mixed content.)

**General settings:**

- Root Directory: `RIO-main/RIO-main/frontend`
- Framework preset: Next.js — Build Command `next build`, Output `.next`
- Node 20 (Vercel default is fine)

Then **redeploy** (Deployments → ⋯ → Redeploy, or just `git push`). A redeploy is
mandatory: `NEXT_PUBLIC_*` values are inlined into the JS bundle at build time, and
`next.config.mjs` bakes the rewrite destination at build time too. Editing an env var
without rebuilding changes nothing.

### What each variable does

- `NEXT_PUBLIC_API_URL` → `src/lib/api.ts`: makes the browser call
  `https://<username>.pythonanywhere.com/api/...` directly, and builds the
  flood image / video URLs from it.
- `BACKEND_URL` → `next.config.mjs`: the same-origin `/api/*` and `/storage/*`
  rewrites. Left at its default `http://127.0.0.1:8000` on Vercel it would break
  any relative call, so set it as a safety net.

### Custom domain (optional)

If you add `www.yourdomain.com` in Vercel, add that origin to `CORS_ORIGINS` on
PythonAnywhere and reload the web app.

---

## 9. Code changes already made for this deployment

| File | Change |
|---|---|
| `backend/pythonanywhere_wsgi.py` | **new** — WSGI entry point (a2wsgi wrapper + env vars) |
| `backend/requirements-pythonanywhere.txt` | **new** — slim, wheel-only dependency set |
| `backend/precompute_flood.py` | **new** — one-off raster cache warmer |
| `backend/app/config.py` | added `CORS_ORIGIN_REGEX` setting |
| `backend/app/main.py` | CORS middleware now honours `CORS_ORIGIN_REGEX` |
| `backend/app/services/flood/raster_pipeline.py` | inventory cached to `storage/flood_cache/inventory.json` (memory + disk), so `/api/flood/meta` doesn't re-scan the rasters on every worker restart |

---

## 10. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `500` on load | Web tab → **Error log** (and `/var/log/<username>.pythonanywhere.com.*.log`). Usually a wrong path in `pythonanywhere_wsgi.py`. |
| `ModuleNotFoundError: app` | Source code / working dir not set to `/home/<username>/RIO/backend`, or venv not selected. |
| Browser: CORS error | Backend `CORS_ORIGINS` doesn't match the Vercel origin, or you forgot to reload the web app after editing it. |
| `/api/flood/meta` says `rasterio not installed` | rasterio missing from the venv — check `pip list` inside `~/.virtualenvs/rio-venv`. |
| `/api/flood/meta` says `file not found in resources/` | `FLOOD_RASTER_DIR` wrong, or `resources/` isn't a sibling of `backend/`. |
| Everything hangs / CPU quota exhausted | You skipped §4. Run `precompute_flood.py`, then reload. |
| Videos 404 | `recordings/` not uploaded or `FLOOD_RECORDINGS_DIR` wrong. |
| Site dead after a while | Free accounts must log in at least every 3 months or the web app is disabled. |

---

## 11. Sanity checklist after deploy

```bash
curl https://<username>.pythonanywhere.com/api/health
curl https://<username>.pythonanywhere.com/api/demo/status/test
curl -I https://<username>.pythonanywhere.com/api/flood/state/depth_max/image.png
```

Then open `https://your-app.vercel.app/flood-3d` — the terrain should drape the
real DEM and the depth layer should appear within a few seconds.
