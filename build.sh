#!/usr/bin/env bash
# build.sh

set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Build completed successfully!"