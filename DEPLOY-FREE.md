# Best free way to host the RIO backend (and connect it to Vercel)

Short answer: **Koyeb free — Docker, always-on, no cold start.** Fallback: **Render free**
(750 h/month, but sleeps after 15 min idle). Both run the Dockerfile that's already in the repo.

---

## 1. Options compared (September 2026)

| Platform | Free allowance | Sleeps / cold start | Card needed | Verdict |
|---|---|---|---|---|
| **Koyeb** | 1 web service, ~512 MB RAM, 0.1 vCPU, 2 GB SSD, free custom domains + CDN | **No — stays up** | Usually no | **Pick this** |
| **Render** | 750 instance-hours/mo, 512 MB RAM, 0.1 vCPU, 100 GB egress | Yes — 15 min idle, ~30–60 s wake | $1 pre-auth | Best fallback |
| Google Cloud Run | 2 M requests + 180 k vCPU-s/mo | Scales to zero, 5–15 s wake | Yes | Excellent if you can enable billing |
| Oracle Cloud Free VM | 4 ARM cores, 24 GB RAM, 200 GB disk, always on | No | Yes (identity verify) | Most power, most sysadmin work |
| Railway | $5 one-off credit | No | Yes | Not free long-term |
| PythonAnywhere | 512 MB disk, 100 CPU-s/day | n/a | No | **Doesn't fit** — see `DEPLOY-PYTHONANYWHERE.md` |

Why Koyeb over Render for this app: your `/flood-3d` page fires several API calls on load. On
Render a sleeping instance makes the first visitor wait up to a minute — bad in a demo. Koyeb's
free container just stays up. Caveat: Koyeb was acquired by Mistral AI in Feb 2026; the free tier
is still there, but keep Render as plan B.

The one thing to know: every free tier gives you **0.1 vCPU**. Reprojecting the HEC-RAS rasters
is slow there, so I made the Dockerfile **bake the raster cache into the image at build time** —
after that, every request (including the first after a restart) is instant.

---

## 2. Deploy on Koyeb (recommended)

1. **Push the repo to GitHub** (Koyeb deploys from GitHub).
   `recordings/` is gitignored, so the videos are not in the image — the app simply reports
   "no videos". See §5 if you want them.
2. **koyeb.com** → *Create app* → **GitHub** → pick the repo.
3. Build settings:
   - Builder: **Docker**
   - Dockerfile location: `RIO-main/RIO-main/backend/Dockerfile`
   - Build context / working directory: **repository root** (the Dockerfile COPYs `resources/`)
   - Port: **8000**, protocol HTTP
4. Instance: the **free / nano or micro (512 MB)** size; region **Frankfurt** (or Washington).
5. **Environment variables** — add just these; the rest are baked into the Dockerfile:

   | Key | Value |
   |---|---|
   | `CORS_ORIGINS` | `https://your-app.vercel.app` |
   | `CORS_ORIGIN_REGEX` | `https://.*\.vercel\.app` |

   (The regex is what makes Vercel **preview** deployments work without touching CORS again.)
6. Health check: `/api/health`.
7. Deploy. First build takes ~4–8 min (pip + rasterio + precompute). Then:

```bash
curl https://<app>.koyeb.app/api/health
curl https://<app>.koyeb.app/api/flood/meta | head -c 300
curl -o /dev/null -w "%{http_code}\n" https://<app>.koyeb.app/api/flood/state/depth_max/image.png
```

Expected: `{"status":"healthy"...}`, a JSON with `"raster_dir":"/app/resources"`, and `200`.

---

## 3. Deploy on Render (fallback)

1. **render.com** → *New* → **Blueprint** → connect the repo. `render.yaml` at the repo root
   defines the service (free plan, Singapore, Dockerfile path, health check).
   Or manually: *New* → **Web Service** → repo → Runtime **Docker** →
   Dockerfile `RIO-main/RIO-main/backend/Dockerfile` → **Free**.
2. Same two env vars as step 5 above.
3. **Kill the cold start**: create a free [UptimeRobot](https://uptimerobot.com) monitor that
   pings `https://<app>.onrender.com/api/health` every 5 minutes. The service never sleeps.
   750 free hours/month ≈ 744 hours in a 31-day month, so **one** always-warm service fits —
   don't add a second one.

---

## 4. Connect the frontend (identical for both hosts)

Vercel project → **Settings → Environment Variables**:

| Name | Value | Environments |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<app>.koyeb.app` (no trailing slash) | Production + Preview |
| `BACKEND_URL` | same value | Production + Preview |

Then **redeploy** — mandatory. `NEXT_PUBLIC_*` is inlined into the JS bundle at build time and
`next.config.mjs` bakes the rewrite destination at build time too, so editing a variable without
rebuilding changes nothing.

Root Directory stays `RIO-main/RIO-main/frontend`. Use `https` (both hosts give free SSL) —
Vercel is HTTPS-only and would block `http` as mixed content.

---

## 5. The videos (93 MB) — optional

`recordings/*.mp4` is gitignored, so it never reaches the build. Two free ways to serve them:

- **In the image**: `git lfs track "recordings/*.mp4"`, commit, then uncomment
  `COPY recordings ./recordings` in the Dockerfile. Adds ~93 MB to the image.
- **From Vercel's CDN (cheaper)**: drop the files in `frontend/public/videos/` and change
  `floodVideoUrl` in `frontend/src/lib/api.ts` to return `/videos/${name}`.

---

## 6. What I changed in the repo

| File | Change |
|---|---|
| `backend/Dockerfile` | dropped the `apt` GDAL step (the rasterio wheel bundles GDAL) → ~250 MB smaller, minutes faster; added container-side `ENV` defaults including `CORS_ORIGIN_REGEX`; added `RUN python precompute_flood.py` so the raster cache is baked into the image |
| `backend/requirements.txt` | removed pandas / scipy / shapely / pyproj / sqlalchemy / alembic / psycopg2 / celery / redis (nothing imports them — ~150 MB saved); **added `pillow`, which was missing** and would have crashed `/api/flood/*` |
| `.dockerignore` | **new** — keeps `node_modules`, `.next`, `recordings`, logs out of the build context |
| `render.yaml` | **new** — one-click Render blueprint (free plan, Singapore, health check, CORS vars) |
| `backend/precompute_flood.py` | **new** — cache warmer, run at image build time |
| `backend/app/config.py`, `app/main.py` | `CORS_ORIGIN_REGEX` support (Vercel preview URLs) |
| `backend/app/services/flood/raster_pipeline.py` | inventory cached to `storage/flood_cache/inventory.json` so `/api/flood/meta` stops rescanning the rasters |

---

## 7. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Build fails on `rasterio` | No wheel for that Python version. Stay on `python:3.11-slim`, or re-enable the `libgdal-dev` apt line (commented in the Dockerfile). |
| Build log says `precompute skipped` | `resources/` wasn't in the build context → wrong build context (must be repo **root**). |
| 502 / "no open port" | Set `PORT` or the service's port to **8000**. |
| CORS error in the browser | `CORS_ORIGINS` doesn't match the Vercel origin, or you added the var but didn't redeploy Vercel. |
| `/api/flood/meta` says `rasterio not installed` | pip step failed; check the build log. |
| `/api/flood/meta` is slow (20 s+) | Precompute didn't run at build; see above. |
| Container OOM-killed | 512 MB is tight if you re-add pandas/scipy — keep requirements slim, or use a paid instance. |
| Render: 30–60 s wait per visit | Expected on the free plan; add the UptimeRobot ping (§3). |

---

## 8. Final checklist

```bash
curl https://<backend>/api/health
curl https://<backend>/api/flood/meta
curl -I https://<backend>/api/flood/state/depth_max/image.png
```

Then open `https://your-app.vercel.app/flood-3d` — real DEM terrain plus the depth layer,
no local machine, no tunnel.
