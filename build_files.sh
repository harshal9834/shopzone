#!/bin/bash
# build_files.sh - Vercel Build Script
# ======================================
# This runs on Vercel during deployment.
set -e  # Exit on any error

echo "=== Installing Python dependencies ==="
python3.12 -m pip install -r requirements.txt

echo "=== Collecting Static Files ==="
# Ensure the staticfiles directory exists so Vercel doesn't error
mkdir -p staticfiles
python3.12 manage.py collectstatic --noinput || echo "Collectstatic failed, but continuing..."

echo "=== Running Migrations ==="
python3.12 manage.py migrate --noinput

echo "=== Build Complete! ==="
