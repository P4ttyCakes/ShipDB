#!/bin/bash

# ShipDB Setup Verification Script

echo "🚢 ShipDB Setup Verification"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "backend/app/main.py" ] || [ ! -f "frontend/index.html" ]; then
    echo "❌ Error: Please run this script from the ShipDB root directory"
    exit 1
fi

echo "✅ Project structure looks correct"

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✅ Python version: $python_version"

# Check if virtual environment can be created
echo "🔧 Testing virtual environment creation..."
cd backend
if python3 -m venv test_venv >/dev/null 2>&1; then
    echo "✅ Virtual environment creation works"
    rm -rf test_venv
else
    echo "❌ Virtual environment creation failed"
    exit 1
fi
cd ..

# Check backend imports
echo "🔧 Testing backend imports..."
cd backend
if python3 -c "from app.main import app; print('✅ Backend imports work')" 2>/dev/null; then
    echo "✅ Backend imports work correctly"
else
    echo "❌ Backend import test failed"
    echo "   Make sure you have the required dependencies installed"
    exit 1
fi
cd ..

# Check frontend structure
echo "🔧 Testing frontend structure..."
if [ -f "frontend/src/main.js" ] && [ -f "frontend/src/App.js" ] && [ -f "frontend/src/styles/main.css" ]; then
    echo "✅ Frontend files are present"
else
    echo "❌ Frontend files are missing"
    exit 1
fi

# Check startup scripts
if [ -f "start_backend.sh" ] && [ -f "start_frontend.sh" ]; then
    echo "✅ Startup scripts are present"
else
    echo "❌ Startup scripts are missing"
    exit 1
fi

# Check if startup scripts are executable
if [ -x "start_backend.sh" ] && [ -x "start_frontend.sh" ]; then
    echo "✅ Startup scripts are executable"
else
    echo "❌ Startup scripts are not executable"
    exit 1
fi

echo ""
echo "🎉 Setup verification complete!"
echo ""
echo "Next steps:"
echo "1. Create a .env file with your API keys (see CONFIGURATION.md)"
echo "2. Run ./start_backend.sh in one terminal"
echo "3. Run ./start_frontend.sh in another terminal"
echo "4. Open http://localhost:8001 in your browser"
echo ""
echo "Backend API docs will be available at: http://localhost:8000/docs"
