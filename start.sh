#!/bin/bash
# Startup script for TrustLink deployment
# Ensures models are initialized before starting the server

echo "Starting TrustLink deployment..."

# Initialize models if they don't exist
echo "Checking for ML models..."
python init_models.py

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --workers 4 --timeout 120 --log-level info
