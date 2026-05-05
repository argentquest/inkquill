# Scripts

## Database operations

| Script | Description |
|--------|-------------|
| `backup_local_postgres.ps1` | Dump the local dev DB to a `.sql` file (no local `pg_dump` needed — runs via Docker). |
| `backup_remote_postgres.ps1` | Dump a PostgreSQL DB from a remote host. |
| `restore_postgres_backup.ps1` | Restore a `.sql` dump into a local database. |
| `clone_postgres_db.ps1` | Clone the local dev DB into local test/prod target databases. |

## Deployment

| Script | Description |
|--------|-------------|
| `deploy_care_circle_docker_host.ps1` | Build and manage the Docker stack on the host (Windows/PowerShell). |
| `deploy_care_circle_docker_host.sh` | Same as above for Ubuntu/Linux. |
| `promote_test_to_prod.ps1` | Build test, verify health, migrate prod, then roll prod forward. |
| `push_local_to_server.ps1` | **First-time server seed**: dump local dev DB + sync uploads to remote server, then restore into Docker environments. |
| `restore_dump_to_env.sh` | Server-side helper: restore a SQL dump into a Docker Compose environment's DB service. |

## Typical first-time server deployment

Run from your Windows dev machine:

```powershell
# 1. Push local dev data to server (seeds both test and prod)
.\scripts\push_local_to_server.ps1 -Server deploy@your-server-ip

# 2. The script prints the next step — SSH in and bring up the stacks:
ssh deploy@your-server-ip
cd ~/inkquill
bash scripts/deploy_care_circle_docker_host.sh -e test -a up -b -d --auto-migrate
bash scripts/deploy_care_circle_docker_host.sh -e prod -a up -b -d --auto-migrate
```

`push_local_to_server.ps1` defaults:
- Dev DB at `localhost:5433` (dev docker-compose)
- Credentials: `inkandquill_dev` / `inkandquill_dev_password`
- Uploads from `runtime/data/uploads/`
- Remote repo at `~/inkquill`
- Remote data at `/srv/care-circle/{test,prod}/`

Override any of these with named parameters — see `-help`.

## Subsequent redeployments (code only, no data migration needed)

```powershell
ssh deploy@your-server-ip "cd ~/inkquill && git pull && bash scripts/deploy_care_circle_docker_host.sh -e prod -a up -b -d"
```

## Subsequent uploads sync only

```powershell
.\scripts\push_local_to_server.ps1 -Server deploy@your-server-ip -SkipDatabase
```

## Database-only refresh (no file sync)

```powershell
.\scripts\push_local_to_server.ps1 -Server deploy@your-server-ip -SkipUploads
```

## Local test/prod database clone (same machine, no SSH)

```powershell
# Clone dev DB into local test and prod databases (used before Docker deployment)
.\scripts\clone_postgres_db.ps1
```

## Seed forum categories (run after first deploy)

```bash
# On the server, inside the backend container:
docker compose exec backend python scripts/seed_forum_categories.py
```

## Care Circle providers

| Script | Description |
|--------|-------------|
| `seed_care_circle_test_families.py` | Seed test families and patients. |
| `import_providers.py` | Import care circle provider definitions. |
| `send_care_circle_newsletter.py` | Manually trigger a newsletter send. |
| `build_care_circle_sample_newsletter.py` | Generate a sample newsletter for preview. |
