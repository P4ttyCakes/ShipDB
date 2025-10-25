#!/bin/bash

# ShipDB API Key Setup Script

echo "🚢 ShipDB API Key Setup"
echo "======================"
echo ""

# Check if .env already exists
if [ -f "backend/.env" ]; then
    echo "⚠️  .env file already exists in backend/"
    echo "   Current ANTHROPIC_API_KEY status:"
    if grep -q "ANTHROPIC_API_KEY=" backend/.env; then
        echo "   ✅ ANTHROPIC_API_KEY is configured"
    else
        echo "   ❌ ANTHROPIC_API_KEY is not configured"
    fi
    echo ""
    echo "Do you want to update it? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo "Please enter your Anthropic API key:"
echo "(You can get one from: https://console.anthropic.com/)"
read -r api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key provided. Setup cancelled."
    exit 1
fi

# Create .env file
cat > backend/.env << EOF
# ShipDB Environment Configuration
ANTHROPIC_API_KEY=$api_key
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Optional: Other API keys
# OPENAI_API_KEY=your_openai_api_key_here
# GEMINI_API_KEY=your_gemini_api_key_here

# AWS Configuration (for deployment)
# AWS_ACCESS_KEY_ID=your_aws_access_key_here
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
# AWS_REGION=us-east-1

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
EOF

echo ""
echo "✅ API key configured successfully!"
echo "   File created: backend/.env"
echo ""
echo "🚀 You can now start the backend:"
echo "   ./start_backend.sh"
echo ""
echo "📝 Note: Keep your API key secure and never commit it to version control!"
