#!/bin/bash
# build_files.sh - Vercel Build Script
# ======================================
# This runs on Vercel during deployment.
echo "=== Starting Build Process ==="

# Exit on any error
set -e

# Use python3 to avoid alias issues
echo "=== Installing Python dependencies ==="
python3 -m pip install -r requirements.txt

echo "=== Collecting Static Files ==="
# Ensure the output directory exists so Vercel doesn't give 'No Output Directory' error
mkdir -p staticfiles
python3 manage.py collectstatic --noinput --clear

echo "=== Running Migrations ==="
python3 manage.py migrate --noinput

echo "=== Build Complete! ==="
