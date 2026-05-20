# Deployment Checkpoint - May 16, 2026

## Goal

Deploy the Ink & Quill app to the Hetzner Ubuntu server using the Docker host deployment path.

## Current Status - May 20, 2026

Production deployment is mostly assembled and the app has been reachable through the domain:

- Domain: `https://app.inkandquill.io`
- Server public IP: `178.104.244.162`
- Host nginx terminates HTTPS and proxies to Docker gateway on local port `38083`.
- Let's Encrypt certificate was issued for `app.inkandquill.io`; cert expires `2026-08-15` and Certbot installed auto-renewal.
- Docker production stack was healthy after database restore and runtime permission fixes.
- Browser login loop was debugged locally and fixed in GitHub.

Latest frontend/auth fixes pushed to `master`:

- `33291cd Fix auth cookie expiration header`
- `013c234 Fix frontend auth redirect loop`
- `5a90525 Fix auth breadcrumb prefetch route`

Next server action after this checkpoint:

```bash
cd /home/eric/inkquill
git pull origin master
bash scripts/deploy_care_circle_docker_host.sh -e prod -a up -b -d
```

Then hard refresh:

```text
https://app.inkandquill.io/auth/login
```

## Server

- Provider: Hetzner
- OS: Ubuntu 24.04.4 LTS
- User: `eric`
- Repo path: `/home/eric/inkquill`
- Public app URL: `https://app.inkandquill.io`
- Public IP verified from server: `178.104.244.162`
- Disk: `/dev/sda1` mounted at `/`, about 150 GB total with about 134 GB free at time of setup

## Local GitHub Checkpoint

Local repo was committed and pushed before deployment work continued, then several deployment/auth fixes were added.

- Branch: `master`
- Remote: `https://github.com/argentquest/inkquill.git`
- Initial deployment checkpoint commit: `a46a14b Checkpoint current workspace before deployment`
- Latest known deployment/auth commit: `5a90525 Fix auth breadcrumb prefetch route`
- Working tree was clean after push on May 20.

## Local Dev Database Backup

A local dev database backup was created before server deployment.

- Database: `inkquill_codebase`
- Backup file: `runtime/artifacts/db-backups/inkquill_codebase_20260516_114208.sql`
- Size: about 24 MB
- Restore command:

```powershell
.\scripts\restore_postgres_backup.ps1 -BackupFile "C:\Code\inkandquill\inkquill\runtime\artifacts\db-backups\inkquill_codebase_20260516_114208.sql"
```

Note: this backup is intentionally not in GitHub because `runtime/` is ignored and may contain private data.

## Server Repo Status

The repo was cloned on the server and switched to `master`.

Current server repo path:

```bash
cd /home/eric/inkquill
```

After switching to `master`, the expected app files were present, including:

- `app`
- `frontendv1`
- `deployments`
- `scripts`
- `docker-compose.yml`
- `DEPLOYMENT_GUIDE.md`

## Server Env Files

The deployment env directory did not exist after clone because it is gitignored, so it was created:

```bash
mkdir -p /home/eric/inkquill/deployments/docker-host/env
```

Created:

- `/home/eric/inkquill/deployments/docker-host/env/prod.host.env`
- `/home/eric/inkquill/deployments/docker-host/env/prod.runtime.env`

`prod.host.env` should contain:

```env
CARE_CIRCLE_PROJECT_NAME=care-circle-prod
CARE_CIRCLE_PUBLIC_PORT=38083
CARE_CIRCLE_BACKEND_PORT=48000
CARE_CIRCLE_DATA_ROOT=/srv/care-circle/prod
CARE_CIRCLE_RUNTIME_ENV_FILE=./env/prod.runtime.env
```

`prod.runtime.env` was created with production values. Do not commit or paste this file because it contains secrets.

Important non-secret URL values were verified:

```env
APP_ENV=production
APP_URL=https://app.inkandquill.io
BACKEND_CORS_ORIGINS=["https://app.inkandquill.io"]
```

## Secret Rotation

During setup, secrets were accidentally pasted into chat. The following were rotated or were requested to be rotated:

- `AUTH_SECRET_KEY` - rotated on server.
- `POSTGRES_PASSWORD` - rotated on server.
- `OPENROUTER_API_KEY` - user said this was done after creating/replacing with a new OpenRouter key.

Do not reuse the exposed values.

## Persistent Data Directories

These server directories were created and ownership was set to `eric:eric`:

```bash
sudo mkdir -p /srv/care-circle/prod/runtime/cache
sudo mkdir -p /srv/care-circle/prod/runtime/logs/backend
sudo mkdir -p /srv/care-circle/prod/runtime/data/uploads
sudo mkdir -p /srv/care-circle/prod/postgres
sudo chown -R eric:eric /srv/care-circle
```

Verified:

```text
/srv/care-circle/prod
├── postgres
└── runtime
```

## Deploy Script

The Linux deploy script exists and was made executable:

```bash
cd /home/eric/inkquill
chmod +x scripts/deploy_care_circle_docker_host.sh
```

Docker Compose config was validated successfully with:

```bash
bash scripts/deploy_care_circle_docker_host.sh -e prod -a config
```

Do not paste full config output in chat because it includes secrets.

## Database Restore And Migration

The original empty/new prod database ran into migration drift because old dev tables and newer migrations overlapped. We decided to restore the local dev database backup into prod instead.

The backup file was copied to the server:

```bash
/home/eric/inkquill_codebase_20260516_114208.sql
```

The prod stack was brought down, `/srv/care-circle/prod/postgres` was emptied with sudo, the DB container was started, and the backup was copied into the container:

```bash
cd /home/eric/inkquill
bash scripts/deploy_care_circle_docker_host.sh -e prod -a down
sudo rm -rf /srv/care-circle/prod/postgres/*
docker compose --project-name care-circle-prod \
  --env-file deployments/docker-host/env/prod.host.env \
  -f deployments/docker-host/docker-compose.base.yml \
  -f deployments/docker-host/docker-compose.prod.yml \
  up -d db
docker cp /home/eric/inkquill_codebase_20260516_114208.sql care-circle-prod-db-1:/tmp/dev_backup.sql
```

After restore, migrations ran cleanly:

```bash
bash scripts/deploy_care_circle_docker_host.sh -e prod -a migrate
```

## Docker Permission Blocker - Resolved

The early Docker socket permission blocker was fixed by adding `eric` to the Docker group and logging in again.

```bash
groups
docker ps
```

Verified `groups` included `docker`, and `docker ps` worked.

## Runtime Upload Permission Blocker - Resolved

Backend initially failed because the container user could not create:

```text
/app/runtime/data/uploads/blog_media
```

Fix was to make the host runtime upload directory writable for the app container user/group, then restart/redeploy. After that, backend became healthy.

## Host Nginx And HTTPS

Host nginx was installed and active:

```bash
nginx -v
certbot --version
sudo systemctl status nginx --no-pager
```

Site config was created at:

```bash
/etc/nginx/sites-available/inkandquill-app
```

It proxies:

```text
app.inkandquill.io -> http://127.0.0.1:38083
```

The site was enabled and nginx config tested:

```bash
sudo ln -s /etc/nginx/sites-available/inkandquill-app /etc/nginx/sites-enabled/inkandquill-app
sudo nginx -t
sudo systemctl reload nginx
```

Certbot succeeded:

```text
Certificate is saved at: /etc/letsencrypt/live/app.inkandquill.io/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/app.inkandquill.io/privkey.pem
```

## Firewall And Ports

The production Docker gateway now exposes:

```text
0.0.0.0:38083->80/tcp
```

UFW included:

- `Nginx Full`
- `38083/tcp`
- `38084/tcp`

Hetzner firewall should allow at least:

- `22/tcp` for SSH
- `80/tcp` for HTTP/Let's Encrypt
- `443/tcp` for HTTPS
- `38083/tcp` only if direct Docker gateway access is still intentionally needed
- `9443/tcp` if Portainer stays exposed

Long term, prefer public traffic through host nginx on `80/443`; direct `38083` can be closed later if no longer needed.

## Production Container Status

After restore and fixes, the prod stack showed healthy containers:

```text
care-circle-prod-backend-1    healthy
care-circle-prod-db-1         healthy
care-circle-prod-frontend-1   healthy
care-circle-prod-gateway-1    healthy, 0.0.0.0:38083->80/tcp
```

Useful commands:

```bash
cd /home/eric/inkquill
bash scripts/deploy_care_circle_docker_host.sh -e prod -a ps
curl -I http://127.0.0.1:38083
curl -I https://app.inkandquill.io
```

## Auth/Login Debugging

Backend login succeeded and returned a valid auth cookie after the cookie expiration fix. `/api/v1/users/me` also returned a valid user when curl reused the cookie.

Browser still looped on login. Local Docker test reproduced the issue. Findings:

- A stale local Docker frontend container was attached to the test network and caused inconsistent Next static chunks locally.
- After removing the stale container and rebuilding, a real frontend auth guard loop remained.
- `AppShellGuard` redirected even when mounted on public/auth routes.
- Breadcrumbs on `/auth/login` created an intermediate `/auth` link; Next prefetch requested `/auth?_rsc=...`, which 404'd.

Fixes pushed:

- `33291cd`: removed invalid cookie `expires` value, keeping `Max-Age`.
- `013c234`: made `AppShellGuard` respect public routes and avoid auth self-redirects.
- `5a90525`: added `/auth` redirect and stopped breadcrumb from linking to missing `/auth`.

Local Docker verification passed:

- `http://localhost:8082/auth/login` showed the login form.
- No `Redirecting to login` loop text.
- Protected route redirected to `/auth/login?next=%2Fstorytelling%2Faccount`.
- No `/auth?_rsc` request was seen after the breadcrumb fix.

## Next Step To Resume

Pull and rebuild the latest frontend/auth fixes on the server:

```bash
cd /home/eric/inkquill
git pull origin master
bash scripts/deploy_care_circle_docker_host.sh -e prod -a up -b -d
```

Then verify:

```bash
curl -I https://app.inkandquill.io/auth/login
curl -s -L -o /dev/null -w "%{http_code} %{url_effective}\n" https://app.inkandquill.io/auth
```

Expected:

- `/auth/login` returns `200`
- `/auth` resolves safely instead of 404
- Browser console should no longer show `GET https://app.inkandquill.io/auth?_rsc=... 404`

After deploy, hard refresh the browser with `Ctrl+F5`.
