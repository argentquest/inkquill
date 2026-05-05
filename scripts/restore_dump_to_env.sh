#!/usr/bin/env bash
# Restore a SQL dump into a Docker-hosted Care Circle environment (test or prod).
# Must be run from the repository root on the server.
# The DB service must be running before calling this script.
set -euo pipefail

usage() {
  echo "Usage: $0 -e <test|prod> -f <dump.sql>"
  echo ""
  echo "  -e, --env    Environment: test or prod"
  echo "  -f, --file   Path to the .sql dump file"
  exit 1
}

ENVIRONMENT=""
DUMP_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -e|--env)  ENVIRONMENT="$2"; shift 2 ;;
    -f|--file) DUMP_FILE="$2";   shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

[[ -z "$ENVIRONMENT" ]] && { echo "Error: -e <test|prod> is required"; usage; }
[[ -z "$DUMP_FILE" ]]   && { echo "Error: -f <dump.sql> is required"; usage; }
[[ -f "$DUMP_FILE" ]]   || { echo "Error: dump file not found: $DUMP_FILE"; exit 1; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_ROOT="$REPO_ROOT/deployments/docker-host"
HOST_ENV_FILE="$DEPLOY_ROOT/env/$ENVIRONMENT.host.env"

[[ -f "$HOST_ENV_FILE" ]] || { echo "Error: $HOST_ENV_FILE not found"; exit 1; }

get_env_value() {
  local file="$1" key="$2"
  grep -E "^\s*${key}=" "$file" | head -1 | cut -d= -f2- | tr -d '"'"'"
}

PROJECT_NAME="$(get_env_value "$HOST_ENV_FILE" CARE_CIRCLE_PROJECT_NAME)"
RUNTIME_ENV_RELATIVE="$(get_env_value "$HOST_ENV_FILE" CARE_CIRCLE_RUNTIME_ENV_FILE)"
RUNTIME_ENV_FILE="$DEPLOY_ROOT/${RUNTIME_ENV_RELATIVE#./}"

[[ -f "$RUNTIME_ENV_FILE" ]] || { echo "Error: $RUNTIME_ENV_FILE not found"; exit 1; }

DB_USER="$(get_env_value "$RUNTIME_ENV_FILE" POSTGRES_USER)"
DB_PASS="$(get_env_value "$RUNTIME_ENV_FILE" POSTGRES_PASSWORD)"
DB_NAME="$(get_env_value "$RUNTIME_ENV_FILE" POSTGRES_DB)"

COMPOSE_ARGS=(
  --project-name "$PROJECT_NAME"
  --env-file "$HOST_ENV_FILE"
  -f "$DEPLOY_ROOT/docker-compose.base.yml"
  -f "$DEPLOY_ROOT/docker-compose.$ENVIRONMENT.yml"
)

echo "Environment : $ENVIRONMENT  (project: $PROJECT_NAME)"
echo "Database    : $DB_NAME  (user: $DB_USER)"
echo "Dump file   : $DUMP_FILE"
echo ""

# Ensure the DB service is running and healthy
docker compose "${COMPOSE_ARGS[@]}" up -d db
echo "Waiting for DB to be healthy..."
for i in $(seq 1 30); do
  STATUS=$(docker compose "${COMPOSE_ARGS[@]}" ps -q db | xargs docker inspect --format='{{.State.Health.Status}}' 2>/dev/null || echo "starting")
  if [[ "$STATUS" == "healthy" ]]; then break; fi
  echo "  ($i/30) status: $STATUS"
  sleep 3
done

run_psql() {
  local db="$1"
  shift
  PGPASSWORD="$DB_PASS" docker compose "${COMPOSE_ARGS[@]}" exec -T db \
    psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$db" "$@"
}

echo "Dropping and recreating '$DB_NAME'..."
run_psql postgres -c "DROP DATABASE IF EXISTS \"$DB_NAME\";"
run_psql postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"

echo "Restoring dump..."
PGPASSWORD="$DB_PASS" docker compose "${COMPOSE_ARGS[@]}" exec -T db \
  psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" < "$DUMP_FILE"

echo ""
echo "Restore complete. '$DB_NAME' is ready in the $ENVIRONMENT environment."
