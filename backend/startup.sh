#!/bin/sh
set -eu

is_enabled() {
  case "$1" in
    1|[Tt][Rr][Uu][Ee]|[Yy][Ee][Ss]|[Oo][Nn])
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

if is_enabled "${RUN_MIGRATIONS_ON_START:-true}"; then
  alembic upgrade head
fi

if is_enabled "${RUN_SEED_ON_START:-true}"; then
  python -m app.setup
fi

exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
