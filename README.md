# 🚢 ShipDB - Instant Cloud Database Deployment

**ShipDB** allows developers to rapidly generate and deploy cloud databases (MongoDB, PostgreSQL, DynamoDB) without manually defining schemas or managing infrastructure.

## 🎯 Target Audience

1. **Developers / Startups**: Spin up production-ready databases for new projects instantly
2. **Rapid Prototyping**: Get a database running in minutes, not hours

## ✨ Features

- **AI-Powered Schema Generation**: Interactive conversation with GPT-5 to understand your requirements
- **Multi-Database Support**: MongoDB, PostgreSQL, and DynamoDB
- **Cloud Deployment**: Automatic AWS deployment (EC2, RDS, DynamoDB)
- **Schema Visualization**: ERD diagrams for visual schema review
- **Export Options**: Download SQL scripts, JSON schemas, and connection info

## 🛠 Tech Stack

### Backend
- **FastAPI** (Python) - High-performance async API
- **GPT-5 via OpenAI** - AI agent for requirements gathering
- **Boto3** - AWS infrastructure management
- **PyMongo, SQLAlchemy, psycopg2** - Database drivers

### Frontend
- **HTML/CSS/JavaScript** (Lovable-friendly)
- **Vanilla JS** - No framework dependencies

## 📁 Project Structure

```
ShipDB/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/routes/   # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── models/       # Pydantic models
│   │   └── utils/        # Helper functions
│   └── tests/            # Test suite
│
├── frontend/             # Lovable HTML/CSS/JS
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── api/          # API client
│   │   └── styles/       # CSS
│   └── index.html
│
└── docs/                 # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- AWS Account with credentials configured
- OpenAI API key (or Anthropic/Gemini API key)

### Installation

```bash
# Clone the repository
git clone https://github.com/P4ttyCakes/ShipDB.git
cd ShipDB

# Create environment file
# See CONFIGURATION.md for detailed setup instructions
# You'll need to create a .env file with your API keys

# Verify setup (optional)
./verify_setup.sh

# Start the application
./start_backend.sh    # In one terminal
./start_frontend.sh   # In another terminal

# Test the API (optional, after starting backend)
python3 test_api.py
```

### Manual Setup (Alternative)

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start backend
uvicorn app.main:app --reload
```

### Frontend

Open `frontend/index.html` in your browser or use a local server:

```bash
cd frontend
python -m http.server 8001
# Open http://localhost:8001
```

## 📖 Usage

1. **Start a Project**: Click "New Project" on the frontend
2. **Answer Questions**: Chat with the AI about your database needs
3. **Review Schema**: View generated schema and ERD diagram
4. **Deploy**: Click deploy to create your AWS database
5. **Connect**: Copy connection info and start coding!

## 🔧 Configuration

See [CONFIGURATION.md](CONFIGURATION.md) for detailed setup instructions including:
- API key setup for OpenAI, Anthropic, and Gemini
- AWS credentials configuration
- Environment variable reference

## 🔧 Troubleshooting

### Common Issues

1. **Backend won't start**: Make sure you have Python 3.10+ and all dependencies installed
2. **Import errors**: Run `./verify_setup.sh` to check your setup
3. **API errors**: Ensure your `.env` file has the correct API keys
4. **Frontend not loading**: Make sure you're running the frontend server on port 8001

### Getting Help

- Check the API documentation at `http://localhost:8000/docs` when the backend is running
- Run `./verify_setup.sh` to diagnose setup issues
- Run `python3 test_api.py` to test API endpoints

## 🤝 Contributing

This is a hackathon MVP. Pull requests welcome!

## 📄 License

MIT

## 🙏 Acknowledgments

Built with love for rapid prototyping and developer productivity.
