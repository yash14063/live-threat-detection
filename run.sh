#!/bin/bash

# ThreatSense Startup Script

echo "====================================="
echo "ThreatSense AI Detection System"
echo "====================================="
echo ""

# Create necessary directories
mkdir -p logs data models storage

# Load environment variables
if [ -f .env ]; then
    echo "✓ Loading environment configuration from .env"
    export $(cat .env | grep -v '#' | xargs)
else
    echo "⚠️  .env file not found. Creating from .env.example"
    cp .env.example .env
    echo "Please edit .env with your configuration and run again."
    exit 1
fi

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from database import init_db; init_db()"

# Start the application
echo ""
echo "Starting ThreatSense..."
echo "API will be available at: http://localhost:8000"
echo "Dashboard: http://localhost:8000/"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
