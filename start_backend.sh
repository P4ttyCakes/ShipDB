#!/bin/bash

# ShipDB Backend Startup Script

echo "🚢 Starting ShipDB Backend..."

# Check if we're in the right directory
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ Error: Please run this script from the ShipDB root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r backend/requirements.txt

# Check for .env file in either backend/.env or repo root .env
if [ -f "backend/.env" ]; then
    ENV_PATH="backend/.env"
elif [ -f ".env" ]; then
    ENV_PATH=".env"
else
    echo "⚠️  Warning: No .env file found. Please create one with your API keys."
    echo "   You can copy backend/env_template.txt to backend/.env and fill in your keys."
fi

# Start the server
echo "🚀 Starting FastAPI server..."
echo "   Backend will be available at: http://localhost:8000"
echo "   API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
