#!/usr/bin/env bash
# Ubuntu / Linux equivalent of deploy_care_circle_docker_host.ps1
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_ROOT="$REPO_ROOT/deployments/docker-host"
FRONTEND_ROOT="$REPO_ROOT/frontendv1"

usage() {
  echo "Usage: $0 -e <test|prod> [-a <up|down|restart|logs|migrate|config|ps|pull>] [-b] [-d] [--auto-migrate] [--verify-frontend]"
  echo ""
  echo "  -e, --env          Environment: test or prod (required)"
  echo "  -a, --action       Action (default: up)"
  echo "  -b, --build        Rebuild images"
  echo "  -d, --detach       Run detached"
  echo "      --auto-migrate Run alembic upgrade before bringing up the stack"
  echo "      --verify-frontend  Run host-side npm run build after deploy"
  exit 1
}

ENVIRONMENT=""
ACTION="up"
BUILD=false
DETACHED=false
AUTO_MIGRATE=false
VERIFY_FRONTEND=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -e|--env)        ENVIRONMENT="$2"; shift 2 ;;
    -a|--action)     ACTION="$2";      shift 2 ;;
    -b|--build)      BUILD=true;       shift   ;;
    -d|--detach)     DETACHED=true;    shift   ;;
    --auto-migrate)  AUTO_MIGRATE=true; shift  ;;
    --verify-frontend) VERIFY_FRONTEND=true; shift ;;
    -h|--help)       usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

[[ -z "$ENVIRONMENT" ]] && { echo "Error: -e <test|prod> is required"; usage; }
[[ "$ENVIRONMENT" != "test" && "$ENVIRONMENT" != "prod" ]] && { echo "Error: environment must be 'test' or 'prod'"; exit 1; }

HOST_ENV_FILE="$DEPLOY_ROOT/env/$ENVIRONMENT.host.env"
BASE_COMPOSE="$DEPLOY_ROOT/docker-compose.base.yml"
ENV_COMPOSE="$DEPLOY_ROOT/docker-compose.$ENVIRONMENT.yml"

[[ -f "$HOST_ENV_FILE" ]] || { echo "Error: $HOST_ENV_FILE not found. Copy the .example file first."; exit 1; }

get_env_value() {
  local file="$1" key="$2"
  grep -E "^\s*${key}=" "$file" | head -1 | cut -d= -f2- | tr -d '"'"'"
}

RUNTIME_ENV_RELATIVE="$(get_env_value "$HOST_ENV_FILE" CARE_CIRCLE_RUNTIME_ENV_FILE)"
[[ -z "$RUNTIME_ENV_RELATIVE" ]] && { echo "Error: CARE_CIRCLE_RUNTIME_ENV_FILE missing from $HOST_ENV_FILE"; exit 1; }

RUNTIME_ENV_FILE="$DEPLOY_ROOT/${RUNTIME_ENV_RELATIVE#./}"
[[ -f "$RUNTIME_ENV_FILE" ]] || { echo "Error: $RUNTIME_ENV_FILE not found. Copy the .example file first."; exit 1; }

PROJECT_NAME="$(get_env_value "$HOST_ENV_FILE" CARE_CIRCLE_PROJECT_NAME)"
[[ -z "$PROJECT_NAME" ]] && { echo "Error: CARE_CIRCLE_PROJECT_NAME missing from $HOST_ENV_FILE"; exit 1; }

DATA_ROOT="$(get_env_value "$HOST_ENV_FILE" CARE_CIRCLE_DATA_ROOT)"
[[ -z "$DATA_ROOT" ]] && { echo "Error: CARE_CIRCLE_DATA_ROOT missing from $HOST_ENV_FILE"; exit 1; }

for dir in \
  "$DATA_ROOT" \
  "$DATA_ROOT/runtime/cache" \
  "$DATA_ROOT/runtime/logs" \
  "$DATA_ROOT/runtime/logs/backend" \
  "$DATA_ROOT/runtime/data/uploads" \
  "$DATA_ROOT/postgres"
do
  mkdir -p "$dir"
done

COMPOSE_ARGS=(
  --project-name "$PROJECT_NAME"
  --env-file "$HOST_ENV_FILE"
  -f "$BASE_COMPOSE"
  -f "$ENV_COMPOSE"
)

invoke_compose() {
  docker compose "${COMPOSE_ARGS[@]}" "$@"
}

invoke_migration() {
  local run_args=(run --rm --no-deps)
  [[ "$BUILD" == true ]] && run_args+=(--build)
  run_args+=(backend alembic upgrade head)
  invoke_compose "${run_args[@]}"
}

cd "$DEPLOY_ROOT"

case "$ACTION" in
  up)
    if [[ "$AUTO_MIGRATE" == true && "$DETACHED" == true ]]; then
      invoke_compose up -d db
      invoke_migration
    fi

    up_args=(up)
    [[ "$BUILD" == true ]]    && up_args+=(--build)
    [[ "$DETACHED" == true ]] && up_args+=(-d)
    invoke_compose "${up_args[@]}"

    if [[ "$DETACHED" == true ]]; then
      invoke_compose restart gateway
    fi

    if [[ "$VERIFY_FRONTEND" == true ]]; then
      cd "$FRONTEND_ROOT"
      npm run build
    fi
    ;;
  down)      invoke_compose down ;;
  restart)   invoke_compose restart ;;
  logs)      docker compose "${COMPOSE_ARGS[@]}" logs -f ;;
  migrate)   invoke_migration ;;
  config)    invoke_compose config ;;
  ps)        invoke_compose ps ;;
  pull)      invoke_compose pull ;;
  *)         echo "Unknown action: $ACTION"; usage ;;
esac
