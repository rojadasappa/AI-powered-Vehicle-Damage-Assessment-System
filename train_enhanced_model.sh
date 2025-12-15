#!/bin/bash

# Enhanced Model Training Script
# This script trains the enhanced severity classification model

echo "Starting Enhanced Model Training..."
echo "=================================="

# Check if data directory exists
if [ ! -d "data/datasets/car_damage_severity" ]; then
    echo "Error: Dataset directory not found!"
    echo "Please ensure the dataset is in data/datasets/car_damage_severity/"
    exit 1
fi

# Create output directory
mkdir -p models/saved_models/severity_enhanced

# Install required packages
echo "Installing required packages..."
pip install albumentations==1.4.0

# Train the enhanced model
echo "Training enhanced model..."
python scripts/train_enhanced_model.py \
    --data data/datasets/car_damage_severity \
    --out models/saved_models/severity_enhanced \
    --test_size 0.2

# Check if training was successful
if [ $? -eq 0 ]; then
    echo "✅ Enhanced model training completed successfully!"
    echo "Model saved to: models/saved_models/severity_enhanced/"
    
    # Display model performance
    if [ -f "models/saved_models/severity_enhanced/report.txt" ]; then
        echo ""
        echo "Model Performance Report:"
        echo "========================="
        cat models/saved_models/severity_enhanced/report.txt
    fi
    
    if [ -f "models/saved_models/severity_enhanced/meta.json" ]; then
        echo ""
        echo "Model Metadata:"
        echo "==============="
        cat models/saved_models/severity_enhanced/meta.json
    fi
else
    echo "❌ Model training failed!"
    exit 1
fi

echo ""
echo "Training completed! You can now use the enhanced model in your application."
