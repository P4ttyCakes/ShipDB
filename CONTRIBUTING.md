# Contributing to ShipDB

Thank you for your interest in contributing to ShipDB! This document will help you get set up and contribute effectively.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- npm or yarn
- Git

### Step 1: Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/ShipDB.git
cd ShipDB
```

### Step 2: Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Frontend Setup

```bash
cd ../frontend
npm install
```

### Step 4: Environment Configuration

```bash
# In the root directory
cp backend/.env.example backend/.env

# Edit backend/.env with your API keys
# At minimum, you need an API key for one AI provider:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY  
# - GOOGLE_API_KEY
```

### Step 5: Run Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit http://localhost:5173 to see the app!

## Making Changes

### Code Style

- **Backend**: Follow PEP 8 for Python code
- **Frontend**: Use ESLint with the provided configuration
- **TypeScript**: Ensure types are properly defined

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend linting
cd frontend
npm run lint
```

### Commit Messages

Use clear, descriptive commit messages:
- `feat: Add color-coded schema visualization`
- `fix: Correct resize handle positioning`
- `docs: Update setup instructions`

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Test your changes thoroughly
4. Run linters/tests
5. Commit with clear messages
6. Push to your fork
7. Create a Pull Request with a clear description

## Project Structure

```
ShipDB/
├── backend/
│   ├── app/
│   │   ├── api/routes/   # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── models/       # Pydantic models
│   │   └── utils/        # Helper functions
│   └── tests/            # Backend tests
│
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── api/          # API client
│   │   └── App.tsx       # Main app
│   └── package.json      # Dependencies
│
└── docs/                 # Documentation
```

## Key Technologies

- **Backend**: FastAPI, Python 3.10+, SQLAlchemy
- **Frontend**: React 18, TypeScript, Vite, ReactFlow
- **AI**: OpenAI GPT, Anthropic Claude, Google Gemini

## Questions?

Open an issue on GitHub with the `question` label, or check existing issues for answers.

Thank you for contributing! 🚀
