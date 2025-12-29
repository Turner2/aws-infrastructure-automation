#!/bin/bash

# Quick test script for AWS Infrastructure Automation
# This script runs all tests and displays results

set -e

echo "=========================================="
echo "  AWS Infrastructure Automation Tests"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
echo -e "${BLUE}Installing/updating dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Run tests with unittest
echo "=========================================="
echo "  Running tests with unittest..."
echo "=========================================="
echo ""
python run_tests.py

echo ""
echo "=========================================="
echo "  Running tests with pytest + coverage..."
echo "=========================================="
echo ""
pytest test_*.py -v --cov=. --cov-report=term-missing --cov-report=html

echo ""
echo "=========================================="
echo -e "${GREEN}✓ All tests completed!${NC}"
echo "=========================================="
echo ""
echo "Coverage report generated in: htmlcov/index.html"
echo "To view: open htmlcov/index.html"
echo ""
