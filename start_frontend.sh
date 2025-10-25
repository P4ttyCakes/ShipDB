#!/bin/bash

# ShipDB Frontend Startup Script

echo "🚢 Starting ShipDB Frontend..."

# Check if we're in the right directory
if [ ! -f "frontend/index.html" ]; then
    echo "❌ Error: Please run this script from the ShipDB root directory"
    exit 1
fi

# Start the frontend server
echo "🚀 Starting frontend server..."
echo "   Frontend will be available at: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd frontend
python3 -m http.server 8001
