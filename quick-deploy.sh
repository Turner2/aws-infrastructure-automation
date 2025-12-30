#!/bin/bash
# Quick deployment script

echo "Starting AWS Infrastructure Deployment..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run deployment
echo ""
echo "Starting deployment..."
python deploy.py

echo ""
echo "Deployment script completed!"
