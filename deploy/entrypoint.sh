#!/usr/bin/env bash
set -euo pipefail

echo "==> Waiting for PostgreSQL..."
python <<'PY'
import os
import sys
import time

host = os.environ.get("POSTGRES_HOST", "")
if not host:
    print("==> No POSTGRES_HOST — skip DB wait")
    sys.exit(0)

import psycopg2

for _ in range(30):
    try:
        psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "bridal"),
            user=os.environ.get("POSTGRES_USER", "bridal"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
            host=host,
            port=os.environ.get("POSTGRES_PORT", "5432"),
        )
        print("==> DB ready")
        break
    except psycopg2.OperationalError:
        time.sleep(2)
else:
    print("FATAL: DB not ready")
    sys.exit(1)
PY

echo "==> Django check + migrate + collectstatic"
if [ "${DJANGO_SETTINGS_MODULE:-}" = "config.settings.production" ]; then
  python manage.py check --deploy
else
  python manage.py check
fi
python manage.py migrate --noinput
python manage.py collectstatic --noinput

_static_count=$(find "${STATIC_ROOT:-/app/staticfiles}" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "==> static files: ${_static_count}"

exec "$@"
