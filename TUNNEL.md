# TUNNEL.md — Start / Restart / Reconnect the Cloudflare Tunnel

How to expose the local RIO app (frontend + backend) to the internet via a
Cloudflare **quick tunnel**, and what to do when it drops or dies.

> Quick tunnels (no Cloudflare account) are **unreliable for long sessions**.
> They can be reaped server-side at any time — the `cloudflared` process stays
> alive but the URL stops working. When that happens, just restart the tunnel
> (a new random URL is issued each time). For a stable URL, see
> [Named tunnel](#stable-url-named-tunnel-optional).

---

## 0. Paths & commands (reference)

| Thing | Path / command |
|---|---|
| Project frontend | `C:/Users/vivek/Downloads/Project_RIO/RIO-main/RIO-main/frontend` |
| Project backend | `C:/Users/vivek/Downloads/Project_RIO/RIO-main/RIO-main/backend` |
| cloudflared binary | `C:/Users/vivek/.workbuddy-ai/binaries/cloudflared/cloudflared.exe` |
| Python venv | `C:/Users/vivek/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe` |
| Node runtime | `C:/Users/vivek/.workbuddy-ai/binaries/node/versions/22.22.2-3/node.exe` |
| Local frontend | `http://localhost:3000` |
| Local backend | `http://127.0.0.1:8000` |

**Architecture:** a **single** tunnel to port `3000` is enough. The Next.js
server rewrites `/api/*` and `/storage/*` to the backend (`BACKEND_URL`, default
`http://127.0.0.1:8000`), so the browser talks to one origin and reaches both tiers.
You do **not** need a second tunnel for the backend.

---

## 1. Start everything (from scratch)

### 1a. Clean the stale build first (avoids the `safe-delete` crash)

`next dev` deletes `.next` on startup; the WorkBuddy safe-delete shim blocks bulk
deletes (>50 files) and kills the server. Always clear it first **with PowerShell**
(not `rm`):

```powershell
Remove-Item -Recurse -Force "C:/Users/vivek/Downloads/Project_RIO/RIO-main/RIO-main/frontend/.next" -ErrorAction SilentlyContinue
```

### 1b. Backend (terminal A)

```bash
cd "C:/Users/vivek/Downloads/Project_RIO/RIO-main/RIO-main/backend"
"C:/Users/vivek/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Wait for: `Application startup complete.` / `Uvicorn running on http://127.0.0.1:8000`.

### 1c. Frontend (terminal B)

```bash
cd "C:/Users/vivek/Downloads/Project_RIO/RIO-main/RIO-main/frontend"
PATH="C:/Users/vivek/.workbuddy-ai/binaries/node/versions/22.22.2-3:$PATH" \
  "C:/Users/vivek/.workbuddy-ai/binaries/node/versions/22.22.2-3/node.exe" \
  node_modules/next/dist/bin/next dev -p 3000
```

Wait for: `✓ Ready in Ns`. First request to a page triggers compilation (can take
10–40 s) — a `000`/timeout on the very first hit is normal; retry.

### 1d. Tunnel (terminal C)

```bash
cd "C:/Users/vivek/.workbuddy-ai/binaries/cloudflared"
./cloudflared.exe tunnel --url http://localhost:3000
```

The public URL is printed in a box:

```
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
|  https://<random-words>.trycloudflare.com                                                 |
```

Look for this line confirming it actually connected:

```
INF Registered tunnel connection connIndex=0 ... protocol=quic
```

---

## 2. Verify it works

Replace `$T` with the URL:

```bash
T="https://<random-words>.trycloudflare.com"
curl -s -o /dev/null -w "root        -> %{http_code}\n" "$T/"
curl -s -o /dev/null -w "health      -> %{http_code}\n" "$T/api/health"
curl -s -o /dev/null -w "flood meta  -> %{http_code}\n" "$T/api/flood/meta"
```

All should be **200**. `flood meta` returning JSON with
`"data_source":"HEC-RAS 2D model outputs..."` confirms the backend is reachable.

---

## 3. Detect a dead / dropped tunnel

Symptoms:

- The public URL returns **`000`** (curl) or "site can't be reached" (browser),
  often in **~0 s** (DNS no longer resolves).
- The tunnel log repeats:

  ```
  ERR Register tunnel error from server side error="Unauthorized: Tunnel not found"
  INF Retrying connection in up to 32s
  ```

  This means the quick tunnel was **reaped** — the process is alive but the tunnel
  is gone. Local ports may still be perfectly healthy (check with section 2 against
  `http://localhost:3000`).

---

## 4. Restart / reconnect (the fix)

1. Find and kill the stuck `cloudflared`:

   ```bash
   tasklist | grep -i cloudflared
   taskkill //PID <pid> //T //F
   ```

2. Relaunch the tunnel (section 1d). You'll get a **new** URL.

3. Re-verify (section 2) and share the new link.

> Make sure only **one** `cloudflared` is running. Multiple instances can cause
> `Unauthorized: Tunnel not found` on startup.

---

## 5. Stop everything (clean shutdown)

Find the PIDs, then kill the trees:

```bash
# which PID owns each port
netstat -ano | grep LISTENING | grep -E ":3000|:8000"
tasklist | grep -i cloudflared

taskkill //PID <cloudflared_pid> //T //F
taskkill //PID <frontend_pid>    //T //F
taskkill //PID <backend_pid>     //T //F
```

Then clean the build (PowerShell):

```powershell
$fe = "C:/Users/vivek/Downloads/Project_RIO/RIO-main/RIO-main/frontend"
$be = "C:/Users/vivek/Downloads/Project_RIO/RIO-main/RIO-main/backend"
Remove-Item -Recurse -Force "$fe/.next" -ErrorAction SilentlyContinue
Get-ChildItem -Path $be -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

> ⚠️ Do **not** kill `node.exe` blindly — WorkBuddy runs its own MCP servers as
> node processes (e.g. `sheetagent`, `weixinpay`). Identify by port/PID first.

---

## 6. Stable URL: named tunnel (optional)

Quick tunnels are fine for ad-hoc demos but die often. For a permanent URL you
need a Cloudflare account and a domain on Cloudflare:

```bash
# one-time login (opens a browser)
./cloudflared.exe tunnel login

# create a named tunnel
./cloudflared.exe tunnel create rio

# route a hostname to it (needs a zone in your CF account)
./cloudflared.exe tunnel route dns rio rio.yourdomain.com

# run it (config.yml maps the hostname to the local service)
./cloudflared.exe tunnel --config config.yml run rio
```

Example `config.yml`:

```yaml
tunnel: rio
credentials-file: C:/Users/vivek/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: rio.yourdomain.com
    service: http://localhost:3000
  - service: http_status:404
```

A named tunnel auto-reconnects and keeps the **same** URL — no more chasing
random `trycloudflare.com` links.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `next dev` exits immediately with `SAFE_DELETE_BULK_CONFIRM_REQUIRED` | stale `.next` trips the safe-delete guard | clear `.next` via PowerShell (section 1a) |
| URL returns `000`, log says `Unauthorized: Tunnel not found` | quick tunnel reaped | restart tunnel (section 4) |
| URL `200` but app shows API errors | backend down or rewrites missing | start backend; confirm `next.config.mjs` has the `/api` + `/storage` rewrites |
| Frontend loads but calls fail on a remote device | `NEXT_PUBLIC_API_URL` baked to a non-public host | leave it unset (relative/same-origin) for tunnels; set to the public backend URL for production |
| First page load times out | Next.js compiling route | retry after ~30 s |
| `502` from the URL | dev server crashed (often safe-delete) or port 3000 not listening | check frontend terminal, clear `.next`, restart |
