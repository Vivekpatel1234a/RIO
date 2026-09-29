"""PythonAnywhere WSGI entry point for the RIO FastAPI backend.

PythonAnywhere's classic "Web" tab expects a WSGI callable. FastAPI is ASGI,
so we wrap it with `a2wsgi`. This is the most stable option on PythonAnywhere
today: it gives you the normal Web tab (static file mappings, reload button,
error log) instead of the experimental ASGI beta.

SETUP — change the two marked constants below, then point the Web tab at this
file (see DEPLOY-PYTHONANYWHERE.md).
"""
import os
import sys

# ---------------------------------------------------------------------------
# CHANGE ME  -----------------------------------------------------------------
USERNAME = "yourusername"          # your PythonAnywhere username
BASE = "/home/yourusername/RIO"    # folder that holds resources/, recordings/
                                   # and backend/
FRONTEND_ORIGIN = "https://your-app.vercel.app"
# ---------------------------------------------------------------------------

BACKEND = os.path.join(BASE, "backend")

# Make `app` importable and ensure relative paths resolve inside the backend.
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)
os.chdir(BACKEND)

# Environment (pydantic-settings reads these at import time).
# Set them here rather than in .env — the WSGI process has a fixed cwd and
# this is guaranteed to be picked up.
os.environ.setdefault("APP_ENV", "production")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("STORAGE_PATH", os.path.join(BACKEND, "storage"))
os.environ.setdefault("DEMO_DATA_PATH", os.path.join(BACKEND, "demo"))
os.environ.setdefault("FLOOD_RASTER_DIR", os.path.join(BASE, "resources"))
os.environ.setdefault("FLOOD_RECORDINGS_DIR", os.path.join(BASE, "recordings"))

# CORS: exact origins + a regex so Vercel preview URLs (*.vercel.app) work.
os.environ.setdefault(
    "CORS_ORIGINS",
    f"{FRONTEND_ORIGIN},http://localhost:3000,http://localhost:3001",
)
os.environ.setdefault("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app")

# ---------------------------------------------------------------------------
# Import AFTER the env vars are set — app.config builds Settings on import.
# ---------------------------------------------------------------------------
from a2wsgi import ASGIMiddleware  # noqa: E402
from app.main import app as asgi_app  # noqa: E402

application = ASGIMiddleware(asgi_app)
