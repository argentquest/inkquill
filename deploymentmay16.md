# Deployment Checkpoint - May 16, 2026

## Goal

Deploy the Ink & Quill app to the Hetzner Ubuntu server using the Docker host deployment path.

## Server

- Provider: Hetzner
- OS: Ubuntu 24.04.4 LTS
- User: `eric`
- Repo path: `/home/eric/inkquill`
- Public app URL currently planned: `http://172.104.244.162:8083`
- Disk: `/dev/sda1` mounted at `/`, about 150 GB total with about 134 GB free at time of setup

## Local GitHub Checkpoint

Local repo was committed and pushed before deployment work continued.

- Branch: `master`
- Remote: `https://github.com/argentquest/inkquill.git`
- Commit: `a46a14b Checkpoint current workspace before deployment`
- Working tree was clean after push.

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
CARE_CIRCLE_PUBLIC_PORT=8083
CARE_CIRCLE_BACKEND_PORT=48000
CARE_CIRCLE_DATA_ROOT=/srv/care-circle/prod
CARE_CIRCLE_RUNTIME_ENV_FILE=./env/prod.runtime.env
```

`prod.runtime.env` was created with production values. Do not commit or paste this file because it contains secrets.

Important non-secret URL values were verified:

```env
APP_URL=http://172.104.244.162:8083
BACKEND_CORS_ORIGINS=["http://172.104.244.162:8083"]
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

## Current Blocker

Starting production failed because the `eric` user did not have Docker socket permission:

```text
unable to get image 'postgres:16-alpine': permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```

## Next Step To Resume

Add `eric` to the Docker group, then log out and back in:

```bash
sudo usermod -aG docker eric
exit
```

After SSH login again, verify:

```bash
groups
docker ps
```

Expected:

- `groups` includes `docker`
- `docker ps` shows a Docker table instead of permission denied

Then retry production deploy:

```bash
cd /home/eric/inkquill
bash scripts/deploy_care_circle_docker_host.sh -e prod -a up -b -d --auto-migrate
```

## Later Steps

After containers start:

```bash
bash scripts/deploy_care_circle_docker_host.sh -e prod -a ps
```

Check local gateway from the server:

```bash
curl -I http://127.0.0.1:8083
```

If using only IP access temporarily, remember the prod gateway is bound to `127.0.0.1:8083` in the Docker host prod compose file, so external browser access may require host nginx or changing the binding intentionally.

For public HTTPS, configure DNS, host nginx, and Certbot as described in `deployments/docker-host/README.md`.
