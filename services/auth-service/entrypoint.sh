#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py create_demo_users || true
python /scripts/register_consul.py || echo "consul register skipped"
if [ $# -eq 0 ]; then
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
else
    exec "$@"
fi

