#!/bin/bash
# Quick cleanup script

echo "Starting AWS Infrastructure Cleanup..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run cleanup
python cleanup.py

echo ""
echo "Cleanup script completed!"
