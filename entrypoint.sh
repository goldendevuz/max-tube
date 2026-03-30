#!/bin/sh
set -e

echo "Preparing directories..."
mkdir -p /app/staticfiles /app/media /app/data

echo "Fixing permissions..."
# root bo‘lsa ishlaydi, bo‘lmasa skip qiladi
chown -R appuser:appuser /app/staticfiles /app/media /app/data 2>/dev/null || true

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
