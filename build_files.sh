#!/bin/bash
# build_files.sh - Vercel Build Script
# ======================================
# This runs on Vercel during deployment.
# It installs dependencies and prepares the app.

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Collecting Static Files ==="
python manage.py collectstatic --noinput

echo "=== Running Migrations ==="
python manage.py migrate

echo "=== Build Complete! ==="
