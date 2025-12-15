#!/bin/bash

# Vehicle Damage Assessment System Setup Script
# This script sets up the virtual environment and installs all dependencies

echo "🚗 Setting up Vehicle Damage Assessment System..."
echo "==============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or later."
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install PyTorch (CPU version)
echo "🧠 Installing PyTorch (CPU version)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install Flask and related packages
echo "🌐 Installing Flask and web packages..."
pip install flask flask-login flask-sqlalchemy flask-migrate

# Install computer vision and ML packages
echo "👁️  Installing computer vision packages..."
pip install opencv-python pillow numpy

# Install PDF generation
echo "📄 Installing PDF generation..."
pip install reportlab

# Install other utilities
echo "🔧 Installing utilities..."
pip install requests

# Create requirements file
echo "📝 Creating requirements file..."
pip freeze > requirements_venv.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p static/uploads
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p models/saved_models

# Set permissions
chmod +x run_app.sh

echo "✅ Setup complete!"
echo "==============================================="
echo "To start the application, run:"
echo "  ./run_app.sh"
echo ""
echo "Or manually activate the environment and run:"
echo "  source .venv/bin/activate"
echo "  python app.py"
echo "==============================================="
