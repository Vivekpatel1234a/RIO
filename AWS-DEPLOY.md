# AWS-DEPLOY.md — RIO backend on AWS EC2

The FastAPI backend is deployed on a single **EC2 t3.micro** instance in
`ap-south-1` (Mumbai), behind **Caddy** for automatic HTTPS, with a stable
**Elastic IP**. No domain is required (HTTPS uses `sslip.io`). Docker is not
used — it's a native Python install under systemd.

## Live URL (stable)

```
https://13-235-165-42.sslip.io
```

Use this as `NEXT_PUBLIC_API_URL` on Vercel. Verified endpoints:

| Endpoint | Result |
|---|---|
| `/api/health` | 200 |
| `/api/flood/meta` | 200 (real HEC-RAS data) |
| `/api/flood/state/depth_max/image.png` | 200 (`image/png`) |

TLS: Let's Encrypt cert for `13-235-165-42.sslip.io` (auto-renewed by Caddy).

> `sslip.io` resolves `13-235-165-42.sslip.io` → `13.235.165.42`. Since the IP is
> an **Elastic IP**, the URL never changes. No DNS/domain needed.

## What was created

| Resource | Value |
|---|---|
| Instance ID | `i-0fd2ca14b9a76f861` |
| Instance type | `t3.micro` (2 vCPU burst, 1 GiB RAM + 2 GiB swap) |
| Region | `ap-south-1` (Mumbai) |
| AMI | Ubuntu 22.04 LTS (`ami-05a7c953f702ad6dd`) |
| Elastic IP | `13.235.165.42` (`eipalloc-07d815016e2eb7ad0`) |
| Security group | `sg-094440810c534e41c` (inbound 22/80/443) |
| SSH key | `rio-ec2` → `C:/Users/vivek/.ssh/rio-ec2.pem` |
| App directory | `/opt/rio` (git clone of `Vivekpatel1234a/RIO`) |
| Python venv | `/opt/rio/venv` |
| Env file | `/etc/rio.env` |
| Services | `rio.service` (uvicorn on 127.0.0.1:8000), `caddy` (443 → 8000) |
| Bootstrap log | `/var/log/rio-bootstrap.log` |

## Estimated cost (~$11/month)

| Item | ~Monthly |
|---|---|
| t3.micro on-demand (ap-south-1) | ~$9.3 |
| 20 GB gp3 EBS | ~$1.8 |
| Elastic IP (attached to a running instance) | $0 |
| Data transfer (low traffic) | ~$0 |
| **Total** | **~$11** |

Cost tips:
- **Stop** the instance when unused: `aws ec2 stop-instances --instance-ids i-0fd2ca14b9a76f861`
  (you still pay for EBS while stopped; the EIP stays free as long as it's attached).
- Cheaper option: switch to **`t4g.micro`** (ARM/Graviton, ~$7.6/mo) — needs an
  `arm64` AMI and ARM wheels (rasterio/numpy/pillow all publish aarch64 wheels).
- A **Reserved Instance / Savings Plan** cuts ~30–40% for 1-year commit.

---

## Wire the Vercel frontend

In **Vercel → Project → Settings → Environment Variables**, add:

| Name | Value | Environments |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://13-235-165-42.sslip.io` | Production, Preview, Development |

Then **redeploy** (env vars are baked at build time for `NEXT_PUBLIC_*`).

The frontend (`src/lib/api.ts`) uses this as the axios base URL and for raster
image/video URLs. CORS on the backend already allows any `https://*.vercel.app`
origin (`CORS_ORIGIN_REGEX`), so preview deploys work too.

> Alternative (no CORS, server-side proxy): set `BACKEND_URL=https://13-235-165-42.sslip.io`
> on Vercel and leave `NEXT_PUBLIC_API_URL` unset — `next.config.mjs` rewrites
> `/api/*` through Vercel's server to the backend.

---

## Operate the server

SSH in:

```bash
ssh -i "C:/Users/vivek/.ssh/rio-ec2.pem" ubuntu@13.235.165.42
```

Common tasks (on the instance):

```bash
sudo systemctl status rio caddy        # service health
sudo journalctl -u rio -n 100 --no-pager   # backend logs
sudo systemctl restart rio             # restart backend
sudo tail -f /var/log/rio-bootstrap.log    # first-boot log
```

### Deploy new code

The instance runs from a git clone, so a redeploy is:

```bash
cd /opt/rio
git pull
/opt/rio/venv/bin/pip install -r RIO-main/RIO-main/backend/requirements.txt   # if deps changed
sudo systemctl restart rio
```

### Change CORS origins

Edit `/etc/rio.env` (e.g. add a custom domain to `CORS_ORIGINS`), then
`sudo systemctl restart rio`.

### Stop / start to save cost

```bash
aws ec2 stop-instances  --instance-ids i-0fd2ca14b9a76f861   # from your PC
aws ec2 start-instances --instance-ids i-0fd2ca14b9a76f861
```

The Elastic IP stays associated, so the URL is unchanged after a restart.

---

## Notes & caveats

- **No Docker.** The `backend/Dockerfile` is still used by Render/Railway/Koyeb;
  EC2 uses a native install (rasterio wheels bundle GDAL, so no apt GDAL needed).
- **1 GiB RAM** is tight; a 2 GiB swap file is configured. If you see OOM during
  heavy raster work, resize to `t3.small` (2 GiB).
- **Certificates** renew automatically via Caddy. Port 80 must stay open for the
  ACME HTTP challenge.
- **Alternative exposure**: you can also run a Cloudflare quick tunnel on the
  instance (`cloudflared tunnel --url http://localhost:8000`), but quick-tunnel
  URLs are random and can be reaped — the `sslip.io` URL above is the stable one.
- **Secrets**: none are stored in the repo; the EC2 key is at
  `C:/Users/vivek/.ssh/rio-ec2.pem` (keep it safe, don't commit it).
