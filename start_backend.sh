#!/bin/bash

# Supabase Deployment Service Startup Script

echo "🚀 Starting Supabase Deployment Service..."

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
cd backend
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: No .env file found."
    echo "   Please create one with:"
    echo "   SUPABASE_URL=https://your-project.supabase.co"
    echo "   SUPABASE_KEY=your-service-key"
fi

# Start the server
echo "🚀 Starting FastAPI server..."
echo "   API will be available at: http://localhost:8000"
echo "   API docs will be available at: http://localhost:8000/docs"
echo ""
echo "📖 To deploy PostgreSQL to Supabase:"
echo "   POST http://localhost:8000/api/postgres"
echo "   Body: {\"sql\": \"CREATE TABLE users (...);\"}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

