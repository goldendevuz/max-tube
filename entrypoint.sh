#!/bin/sh
set -e

echo "Preparing directories..."
mkdir -p /app/staticfiles /app/media /app/data

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput || true

echo "Starting server..."
exec "$@"
