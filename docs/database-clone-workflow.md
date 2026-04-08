# Database Clone Workflow

This repository now includes a repeatable PostgreSQL clone script:

`scripts/clone_postgres_db.ps1`

It clones the current development database into separate target databases on the same PostgreSQL server.

## Default behavior

If you run the script with no arguments, it uses:

- source database: `POSTGRES_DB` from `.env`
- target databases: `<source>_test` and `<source>_prod`

With the current `.env`, that means:

- source: `inkquill_codebase`
- targets: `inkquill_codebase_test`, `inkquill_codebase_prod`

The Docker overrides now use those clone targets automatically:

- [docker-compose.test.yml](C:/code2025a/inbkandquill2/docker-compose.test.yml) -> `POSTGRES_TEST_DB`
- [docker-compose.prod.yml](C:/code2025a/inbkandquill2/docker-compose.prod.yml) -> `POSTGRES_PROD_DB`

## Run it

```powershell
.\scripts\clone_postgres_db.ps1
```

If the target databases already exist and you want to replace them:

```powershell
.\scripts\clone_postgres_db.ps1 -Force
```

## Notes

- The script uses a temporary `postgres:16-alpine` Docker container as the `pg_dump` and `psql` client.
- Localhost database hosts are translated to `host.docker.internal` so the Docker client container can reach your local PostgreSQL server.
- Dumps are written to `artifacts/db-clones/`.
- `-Force` drops and recreates target databases before restore.
- This is safe for creating isolated `test` and `prod` clones on the same server, but it will overwrite the target databases when `-Force` is used.
