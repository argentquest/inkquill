# Care Circle Docker Host Deployment

This bundle is for running **Care Circle test and production** on a single Docker server.

It assumes:

- one Docker host
- one repo checkout
- separate `test` and `prod` deployments
- separate persistent directories per environment

## Files

- `docker-compose.base.yml`: common stack definition
- `docker-compose.test.yml`: test-only host port bindings
- `docker-compose.prod.yml`: prod-only host port bindings
- `nginx/app.conf`: reverse proxy config
- `env/*.example`: example host-level and runtime env files

## Stack

The stack contains:

- `gateway`
- `frontend`
- `backend`
- `db`

The scheduler runs as a **standalone host process** (not in Docker). Start it with:

```bash
python -m app.scheduler.main
```

The frontend container reaches it via `host.docker.internal:8001` (configured by `SCHEDULER_BASE_URL` in the compose file).

## Persistent data

Each environment should have its own host directory tree.

Suggested layout:

```text
/srv/care-circle/
  test/
    cache/
    logs/
      backend/
    postgres/
  prod/
    cache/
    logs/
      backend/
    postgres/
```

## First-time setup

1. Copy the example host env file for the environment.
2. Copy the example runtime env file for the environment.
3. Fill in the real secrets and URLs.
4. Create the data directories on the host.
5. Use the deployment script in `scripts/deploy_care_circle_docker_host.ps1`.

## Commands

Standard test bring-up:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_care_circle_docker_host.ps1 -Environment test -Action up -Build -Detached
```

One-command first-time test bootstrap with automatic migration:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_care_circle_docker_host.ps1 -Environment test -Action up -Build -Detached -AutoMigrate
```

Same flow with an extra host-side frontend production build verification after deployment:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_care_circle_docker_host.ps1 -Environment test -Action up -Build -Detached -AutoMigrate -VerifyFrontendBuild
```

Manual migration only:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_care_circle_docker_host.ps1 -Environment test -Action migrate
```

Notes:

- `-AutoMigrate` is intended for detached `up` runs.
- With `-AutoMigrate`, the script starts `db`, runs Alembic using the backend image, then starts the full stack.
- The gateway is restarted after detached startup so nginx refreshes Docker DNS for recreated upstream containers.
- `-VerifyFrontendBuild` runs a host-side `npm run build` in `frontendv1/` after deployment succeeds.

## Notes

- The scheduler process requires Python Playwright (Chromium) for newsletter PDF generation — see `Dockerfile.scheduler` for the full dependency list.
- The backend container mounts `CARE_CIRCLE_DATA_ROOT/cache` at `/app/cache`. The standalone scheduler should be configured with the same host path so newsletter artifacts are shared.
