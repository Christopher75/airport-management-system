#!/usr/bin/env bash
# Render.com build script
# This script runs during every deploy

set -o errexit  # Exit on error

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate --no-input

echo "==> Build complete!"
