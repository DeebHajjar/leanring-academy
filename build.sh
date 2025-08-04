#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Update pip to latest version
echo "Updating pip..."
pip install --upgrade pip

# Install system dependencies for PostgreSQL
echo "Installing system dependencies..."
apt-get update
apt-get install -y libpq-dev

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Verify critical packages
echo "Verifying package installations..."
python -c "import psycopg2; print('✅ psycopg2 installed successfully')" || echo "❌ psycopg2 failed"
python -c "import django; print('✅ Django installed successfully')" || echo "❌ Django failed"
python -c "import dj_database_url; print('✅ dj-database-url installed successfully')" || echo "❌ dj-database-url failed"

# Check Django configuration
echo "Checking Django configuration..."
python manage.py check --deploy

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print('✅ Superuser created successfully')
else:
    print('ℹ️ Superuser already exists')
"

echo "Build completed successfully!"
