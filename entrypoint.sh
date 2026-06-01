#!/bin/sh
set -e

echo "Preparing directories..."

mkdir -p \
    /app/db \
    /app/staticfiles \
    /app/media \
    /app/data

touch /app/db/db.sqlite3

echo "Running migrations..."
make migrate || python manage.py migrate --noinput

echo "Collecting static..."
make collectstatic || python manage.py collectstatic --noinput || true

echo "Starting server..."
exec "$@"
