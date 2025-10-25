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
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/P4ttyCakes/ShipDB.git
cd ShipDB

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

Set these environment variables:

```env
OPENAI_API_KEY=your_key_here
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

## 🤝 Contributing

This is a hackathon MVP. Pull requests welcome!

## 📄 License

MIT

## 🙏 Acknowledgments

Built with love for rapid prototyping and developer productivity.
