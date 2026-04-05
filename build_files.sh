#!/bin/bash
# build_files.sh - Vercel Build Script
# ======================================
echo "=== Starting Build Process ==="

# Exit on any error
set -e

# Install dependencies using the --break-system-packages flag for Vercel's environment
echo "=== Installing Python dependencies ==="
python3 -m pip install -r requirements.txt --break-system-packages

echo "=== Collecting Static Files ==="
# Explicitly create the directory and run collectstatic
mkdir -p staticfiles
python3 manage.py collectstatic --noinput --clear

echo "=== Running Migrations ==="
python3 manage.py migrate --noinput

echo "=== Build Complete! ==="
# Final check to ensure the directory exists for Vercel
ls -d staticfiles
