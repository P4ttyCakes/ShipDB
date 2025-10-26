# Setup Guide for ShipDB

## Quick Start

Follow these steps to get ShipDB running on your machine:

### 1. Clone the Repository

```bash
git clone https://github.com/P4ttyCakes/ShipDB.git
cd ShipDB
```

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with your API keys
# You'll need:
# - OPENAI_API_KEY (or ANTHROPIC_API_KEY, GOOGLE_API_KEY)
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
```

### 4. Frontend Setup

```bash
cd ../frontend
npm install
```

### 5. Start the Application

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

### 6. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Troubleshooting

### Backend Issues

- **Module not found**: Make sure you're in the virtual environment (`source venv/bin/activate`)
- **Port already in use**: Change the port in `uvicorn app.main:app --reload --port 8001`

### Frontend Issues

- **Port already in use**: Vite will automatically try another port
- **Node modules error**: Run `npm install` again
- **Type errors**: Make sure you have TypeScript installed (`npm install -g typescript`)

### API Connection Issues

- Make sure the backend is running on port 8000
- Check that your `.env` file has the correct API keys
- Verify the API is responding at http://localhost:8000/docs

## Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload
2. **Type Checking**: Run `npm run lint` in frontend directory
3. **API Testing**: Use the interactive docs at http://localhost:8000/docs

## Next Steps

- Read the main [README.md](README.md) for feature overview
- Check [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration
- Explore the interactive schema visualization features
