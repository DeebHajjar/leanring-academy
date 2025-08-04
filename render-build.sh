#!/usr/bin/env bash
# Simple build script for Render
set -o errexit

echo "🚀 Starting Render build..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate

echo "✅ Build completed successfully!"
