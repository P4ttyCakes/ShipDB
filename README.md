# ShipDB

ShipDB fully automates the database pipeline for new startup and business founders, helping design, visualize, and deploy schemas with a FastAPI backend and a React + TypeScript frontend.

Current support for Supabase and AWS deployment, with PostgreSQL, DynamoDB, and JSON schema code provided. 

## Authors 

Created by Ahaan Shah <ahaansh@umich.edu>, Patrick Lu <Patlu@umich.edu>, and Nick Wang <wangnick@umich.edu>

## Tech stack

- Backend: FastAPI (Python), Pydantic, Uvicorn
- Services: PostgreSQL, DynamoDB, AWS, Supabase deployment services
- Frontend: React 18, TypeScript, Vite, TailwindCSS, shadcn/ui

## Project structure

```
ShipDB/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── deploy.py
│   │   │       ├── projects.py
│   │   │       ├── schema.py
│   │   │       └── visualization.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── main.py
│   │   ├── models/
│   │   │   └── deployment.py
│   │   └── services/
│   │       ├── ai_agent.py
│   │       ├── schema_generator.py
│   │       └── deployment/
│   │           ├── base.py
│   │           ├── factory.py
│   │           ├── manager.py
│   │           ├── dynamodb.py
│   │           ├── dynamodb_service.py
│   │           ├── postgresql.py
│   │           ├── postgresql_service.py
│   │           └── supabase_service.py
│   ├── requirements.txt
│   └── venv/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChartDBViewer.tsx
│   │   │   ├── InteractiveSchemaVisualization.tsx
│   │   │   ├── SchemaVisualization.tsx
│   │   │   └── ui/ (shadcn components)
│   │   ├── pages/
│   │   │   ├── Chat.tsx
│   │   │   ├── Index.tsx
│   │   │   └── NotFound.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── start_backend.sh
├── start_frontend.sh
├── CONFIGURATION.md
├── SETUP.md
└── SUPABASE_INTEGRATION.md
```

## Key backend components

- `app/main.py`: FastAPI app entry point
- `app/api/routes/*.py`: API endpoints for deploy, projects, schema, visualization
- `app/services/ai_agent.py`: AI-driven requirements parsing and schema guidance
- `app/services/deployment/*`: Deployment abstractions and providers (PostgreSQL, DynamoDB, Supabase)
- `app/services/schema_generator.py`: Schema generation utilities

## Key frontend components

- `src/components/SchemaVisualization.tsx` and `InteractiveSchemaVisualization.tsx`: schema/ERD views
- `src/components/ChartDBViewer.tsx`: chart-based table view
- `src/components/ui/*`: shadcn/ui primitives
- `src/pages/*`: main routes (chat, index, not found)

## Getting started

Prerequisites: Python 3.12+, Node.js 18+.

Using the helper scripts (recommended):

```bash
./start_backend.sh   # starts FastAPI (Uvicorn)
./start_frontend.sh  # starts Vite dev server
```

Manual setup (alternative):

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev
```

API docs are available at `http://localhost:8000/docs` when the backend is running. The frontend dev server defaults to `http://localhost:5173`.

## Configuration

See `CONFIGURATION.md`, `SETUP.md`, and `SUPABASE_INTEGRATION.md` for environment variables, provider setup, and credentials.


