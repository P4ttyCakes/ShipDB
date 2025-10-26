#!/bin/bash

# ShipDB Frontend Startup Script

echo "🚢 Starting ShipDB Frontend..."

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the ShipDB root directory"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start the frontend server
echo "🚀 Starting frontend server..."
echo "   Frontend will be available at: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd frontend
npm run dev
