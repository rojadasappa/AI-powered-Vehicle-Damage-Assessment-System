#!/bin/bash

# Vehicle Damage Assessment System Startup Script
# This script activates the virtual environment and runs the Flask application

echo "🚗 Starting Vehicle Damage Assessment System..."
echo "=============================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup_venv.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import torch, flask, cv2, reportlab" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Please run: pip install -r requirements_venv.txt"
    exit 1
fi

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create necessary directories
mkdir -p static/uploads
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images

# Initialize database if needed
echo "🗄️  Initializing database..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database initialized')
"

# Start the Flask application
echo "🚀 Starting Flask application on http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo "=============================================="

python app.py
