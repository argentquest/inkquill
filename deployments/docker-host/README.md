# Care Circle Docker Host Deployment

This bundle runs **Care Circle test and production** on a single Docker host (Ubuntu or any Linux server running Docker).

It assumes:

- one Docker host
- one repo checkout
- separate `test` and `prod` deployments
- separate persistent directories per environment

## Files

- `docker-compose.base.yml`: common stack definition (backend, frontend, gateway, db)
- `docker-compose.test.yml`: test-only host port bindings
- `docker-compose.prod.yml`: prod-only host port bindings
- `nginx/app.conf`: in-stack reverse proxy config
- `env/*.example`: example host-level and runtime env files

## Stack

| Service | Description |
|---------|-------------|
| `gateway` | nginx reverse proxy — the only service with a host port |
| `frontend` | Next.js production build |
| `backend` | FastAPI (Gunicorn + Uvicorn) |
| `db` | PostgreSQL 16 |

The scheduler runs as a **standalone host process** (not in Docker). Start it with:

```bash
python -m app.scheduler.main
```

The frontend container reaches it via `host.docker.internal:8001` (configured by `SCHEDULER_BASE_URL` in the compose file).

## Persistent data

Each environment has its own host directory tree. The backend mounts three paths:

| Host path | Container path | Contents |
|-----------|----------------|----------|
| `CARE_CIRCLE_DATA_ROOT/runtime/cache` | `/app/runtime/cache` | AI + newsletter cache |
| `CARE_CIRCLE_DATA_ROOT/runtime/logs/backend` | `/app/runtime/logs` | Backend log files |
| `CARE_CIRCLE_DATA_ROOT/runtime/data/uploads` | `/app/runtime/data/uploads` | Blog media and story uploads |
| `CARE_CIRCLE_DATA_ROOT/postgres` | `/var/lib/postgresql/data` | Database files |

Suggested layout:

```text
/srv/care-circle/
  test/
    runtime/
      cache/
      logs/
        backend/
      data/
        uploads/
    postgres/
  prod/
    runtime/
      cache/
      logs/
        backend/
      data/
        uploads/
    postgres/
```

## First-time server bootstrap (complete checklist)

Everything the server needs falls into three categories:
- **Repo code** — delivered by `git clone`
- **Secret env files** — created manually from the examples (gitignored, never in the repo)
- **Data** — database content + uploaded files, pushed from the dev machine

### Step 1 — On the server: install Docker and clone the repo

```bash
# Install Docker (Ubuntu 22.04/24.04)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER   # log out and back in after this

# Clone the repo
git clone git@github.com:your-org/inkquill.git ~/inkquill
cd ~/inkquill
```

### Step 2 — On the server: create the env files

The env files are gitignored. Copy the examples and fill in real secrets:

```bash
cd ~/inkquill/deployments/docker-host

# Test environment
cp env/test.host.env.example env/test.host.env
cp env/test.runtime.env.example env/test.runtime.env

# Production environment
cp env/prod.host.env.example env/prod.host.env
cp env/prod.runtime.env.example env/prod.runtime.env
```

Edit each file and set at minimum:
- `POSTGRES_PASSWORD` — choose a strong password (same value in both host and runtime env)
- `APP_URL` — the public URL (e.g. `https://care-circle.example.com` for prod, `http://your-server:8082` for test)
- `AUTH_SECRET_KEY` — generate with: `python3 -c "import secrets; print(secrets.token_hex(32))"`
- `OPENROUTER_API_KEY` — your OpenRouter key
- `BACKEND_CORS_ORIGINS` — must match `APP_URL`

### Step 3 — On the dev machine: push local data to the server

This dumps the local dev database and syncs local uploads to both test and prod on the server:

```powershell
# From Windows dev machine (PowerShell)
.\scripts\push_local_to_server.ps1 -Server deploy@your-server-ip
```

What it does:
1. Dumps the local dev DB (port 5433) to a `.sql` file
2. SCPs the dump to the server
3. SSHs in and restores the dump into both the test and prod Docker databases
4. Rsyncs `runtime/data/uploads/` to `/srv/care-circle/{test,prod}/runtime/data/uploads/`

See `scripts/push_local_to_server.ps1 -?` for all parameters (custom ports, SSH keys, skip flags).

### Step 4 — On the server: start the stacks

```bash
cd ~/inkquill
bash scripts/deploy_care_circle_docker_host.sh -e test -a up -b -d --auto-migrate
bash scripts/deploy_care_circle_docker_host.sh -e prod -a up -b -d --auto-migrate
```

`--auto-migrate` applies Alembic migrations before the stack comes up. Use it on first deploy and after any code update that includes schema changes.

### What goes where (summary)

| What | How it gets to the server |
|------|--------------------------|
| Application code | `git clone` / `git pull` |
| `env/test.host.env` | Manually created from example (Step 2) |
| `env/test.runtime.env` | Manually created from example (Step 2) |
| `env/prod.host.env` | Manually created from example (Step 2) |
| `env/prod.runtime.env` | Manually created from example (Step 2) |
| Database content | `push_local_to_server.ps1` (Step 3) |
| Uploaded media files | `push_local_to_server.ps1` (Step 3) |

## HTTPS with Let's Encrypt (production)

**Prerequisite:** you must have a domain name with its DNS A record pointing at your server IP.
Let's Encrypt cannot issue certificates for bare IP addresses.

### Architecture

```
Browser
  │
  ├─ :80  ─→ host nginx ─→ 301 redirect to HTTPS
  │
  └─ :443 ─→ host nginx (TLS, Let's Encrypt cert)
               │
               └─ 127.0.0.1:8083 ─→ Docker nginx (HTTP, loopback only)
                                       ├─ /api/  → backend:8000
                                       ├─ /uploads/ → backend:8000
                                       └─ /     → frontend:3000
```

Port 8083 is bound to `127.0.0.1` in `docker-compose.prod.yml` — it is **not reachable from outside the server**.
The only public entry points are ports 80 (redirect) and 443 (HTTPS), owned by the host nginx.

> **Note on Docker + UFW:** Docker bypasses UFW by writing iptables rules directly. Binding to `127.0.0.1` in the compose file is the correct way to restrict access — a UFW `deny 8083` rule alone would not work.

### Step A — Install nginx and Certbot on the host

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

Verify nginx is running:

```bash
sudo systemctl status nginx
```

### Step B — Open firewall ports

```bash
sudo ufw allow 'Nginx Full'   # opens 80 and 443
sudo ufw status
```

### Step C — Create the host nginx vhost

Replace `yourdomain.com` with your actual domain:

```bash
sudo nano /etc/nginx/sites-available/care-circle
```

Paste this content:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    # Certbot will add the HTTPS redirect here automatically
}
```

Enable the site and test the config:

```bash
sudo ln -s /etc/nginx/sites-available/care-circle /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Step D — Obtain the certificate

```bash
sudo certbot --nginx -d yourdomain.com
```

Certbot will:
1. Verify you own the domain (via the HTTP challenge on port 80)
2. Issue the certificate
3. Automatically rewrite your nginx vhost to add the HTTPS block and HTTP→HTTPS redirect

After it finishes, open `/etc/nginx/sites-available/care-circle` — it will look something like this (Certbot fills in the SSL lines):

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 50m;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    location / {
        proxy_pass         http://127.0.0.1:8083;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto https;
        proxy_read_timeout 300s;
    }
}
```

If the HSTS and proxy headers are not added by Certbot, add them manually and run `sudo nginx -t && sudo systemctl reload nginx`.

### Step E — Update the prod runtime env

The app needs to know it is now running under HTTPS:

```bash
nano ~/inkquill/deployments/docker-host/env/prod.runtime.env
```

Update:

```
APP_URL=https://yourdomain.com
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
SOCIAL_AUTH_REDIRECT_IS_HTTPS=true
```

### Step F — Restart the prod stack to pick up the new env

```bash
cd ~/inkquill
bash scripts/deploy_care_circle_docker_host.sh -e prod -a restart
```

### Step G — Enable HSTS inside the Docker nginx

Now that HTTPS is active, uncomment the HSTS header in the inner proxy config:

```bash
nano ~/inkquill/deployments/docker-host/nginx/app.conf
```

Find and uncomment this line:

```nginx
# add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

Remove the `#` so it reads:

```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

Then restart the gateway container to apply the change:

```bash
docker compose -p care-circle-prod \
  --env-file ~/inkquill/deployments/docker-host/env/prod.host.env \
  -f ~/inkquill/deployments/docker-host/docker-compose.base.yml \
  -f ~/inkquill/deployments/docker-host/docker-compose.prod.yml \
  restart gateway
```

### Step H — Verify auto-renewal

Certbot installs a systemd timer that renews certificates automatically before they expire.
Check it is active:

```bash
sudo systemctl status certbot.timer
```

Test the renewal process (dry run, makes no changes):

```bash
sudo certbot renew --dry-run
```

Certificates are valid for 90 days and are renewed automatically at ~60 days.
You do not need to do anything further — Certbot and nginx handle it.

## Commands (Linux / Ubuntu)

Standard test bring-up:

```bash
bash scripts/deploy_care_circle_docker_host.sh -e test -a up -b -d
```

First-time bootstrap with automatic migration:

```bash
bash scripts/deploy_care_circle_docker_host.sh -e test -a up -b -d --auto-migrate
```

Production deploy:

```bash
bash scripts/deploy_care_circle_docker_host.sh -e prod -a up -b -d --auto-migrate
```

Manual migration only:

```bash
bash scripts/deploy_care_circle_docker_host.sh -e prod -a migrate
```

View logs:

```bash
bash scripts/deploy_care_circle_docker_host.sh -e prod -a logs
```

## Commands (Windows PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_care_circle_docker_host.ps1 -Environment test -Action up -Build -Detached -AutoMigrate
```

## Firewall (UFW)

```bash
sudo ufw allow OpenSSH          # port 22 — never lock yourself out
sudo ufw allow 'Nginx Full'     # ports 80 (HTTP) + 443 (HTTPS)
sudo ufw enable
sudo ufw status
```

Expected final state:

```
To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
Nginx Full                 ALLOW       Anywhere
```

**Do not open ports 8082 or 8083.** The test stack (8082) is accessible directly since it uses `0.0.0.0` binding and is for internal use only. The prod stack (8083) is bound to `127.0.0.1` in `docker-compose.prod.yml` so it cannot be reached externally regardless of the firewall.

## SMTP outbound (email)

The app sends email via SMTP (port 587, STARTTLS). Many VPS providers block outbound port 587 and 25 by default to prevent spam abuse.

**Step 1 — Check if port 587 is blocked:**

```bash
nc -zv smtp.ionos.com 587
```

If it hangs or reports "Connection refused", your provider is blocking it.

**Step 2 — Unblock with your VPS provider:**

Most providers have a support ticket or control panel option to unblock outbound SMTP. Common labels:
- "Remove SMTP block" / "Lift port 25/587 restriction"
- Hetzner: open a support ticket with a brief description of your use case
- DigitalOcean: account must be older than 60 days, then request via support
- OVH/Ionos VPS: support ticket or firewall rule in the control panel

**Step 3 — Allow outbound 587 in UFW (if UFW is blocking it):**

UFW's default outgoing policy is `allow`, so this is usually not needed. If you have changed the default outgoing policy to `deny`, add:

```bash
sudo ufw allow out 587/tcp
sudo ufw allow out 465/tcp   # SMTP over TLS (alternative port)
```

**Step 4 — Test from the server:**

```bash
nc -zv smtp.ionos.com 587 && echo "Port 587 is open"
```

**Step 5 — Verify the runtime env has correct SMTP credentials:**

```bash
nano ~/inkquill/deployments/docker-host/env/prod.runtime.env
```

Confirm these are set:
```
SMTP_SERVER=smtp.ionos.com
SMTP_PORT=587
SMTP_USERNAME=notification@inkandquill.io
SMTP_PASSWORD=your-password
FROM_EMAIL=notification@inkandquill.io
FROM_NAME=Ink & Quill
EMAIL_TEST_MODE=false
```

Restart the backend to pick up any changes:

```bash
cd ~/inkquill
bash scripts/deploy_care_circle_docker_host.sh -e prod -a restart
```

## Database backups

Schedule a daily dump with cron:

```bash
crontab -e
# Add:
0 3 * * * docker exec care-circle-prod-db-1 pg_dump -U care_circle_prod care_circle_prod | gzip > /srv/backups/care-circle-prod-$(date +\%Y\%m\%d).sql.gz
```

Keep at least 7 days of backups. Test restores periodically.

## GitHub Actions self-hosted runner (CI/CD)

The workflow (`.github/workflows/promote-test-to-prod.yml`) uses a `self-hosted` runner. Register one on your Ubuntu host:

```bash
# Follow the GitHub UI: Settings → Actions → Runners → New self-hosted runner
# Choose Linux, follow the download + configure steps
sudo ./svc.sh install && sudo ./svc.sh start
```

The runner process needs Docker access — add the runner user to the `docker` group:

```bash
sudo usermod -aG docker <runner-user>
```

## Notes

- The scheduler process requires Python Playwright (Chromium) for newsletter PDF generation — see `Dockerfile.scheduler` for the full dependency list.
- The backend and scheduler must share the same `CARE_CIRCLE_DATA_ROOT/runtime/cache` path so newsletter artifacts are accessible to both.
- `runtime.env` files are gitignored (`env/.gitignore`) — never commit real secrets.
