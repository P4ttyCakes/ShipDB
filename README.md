# 🚢 ShipDB - Universal Database Architect

**ShipDB** is a WORLD-CLASS database architect that creates DETAILED, FOOL-PROOF, DEPLOYABLE databases for ANY business sector. From simple startups to enterprise platforms, ShipDB eliminates ALL database complexity while providing the RIGHT level of sophistication for your needs.

## 🎯 Universal Business Support

ShipDB understands and creates perfect databases for **EVERY** business sector:

- **🏥 Healthcare & Medical** - HIPAA compliance, patient records, appointments
- **💰 Finance & Banking** - PCI compliance, transactions, security
- **🏭 Manufacturing & Supply Chain** - Inventory, suppliers, quality control
- **🛒 E-commerce & Retail** - Products, orders, payments, inventory
- **🏠 Real Estate & Property** - Listings, agents, transactions
- **🎓 Education & Learning** - Students, courses, assessments
- **🎬 Media & Entertainment** - Content, subscriptions, analytics
- **💼 Professional Services** - Clients, projects, billing
- **🏛️ Government & Public Sector** - Citizens, services, compliance
- **💻 SaaS & Technology** - Multi-tenancy, subscriptions, APIs
- **🏨 Hospitality & Tourism** - Bookings, guests, services
- **🌾 Agriculture & Food** - Crops, suppliers, traceability
- **🚚 Transportation & Logistics** - Vehicles, routes, tracking
- **⚡ Energy & Utilities** - Customers, usage, billing
- **⚖️ Legal & Law** - Cases, clients, documents
- **📈 Marketing & Advertising** - Campaigns, leads, ROI
- **👥 Human Resources** - Employees, payroll, performance
- **And ANY other business sector or use case!**

## ✨ Enhanced Features

- **🤖 AI-Powered Universal Design**: Adapts to ANY business type and size
- **📊 Comprehensive Database Features**: 
  - Complete CRUD operations with proper relationships
  - User management and authentication
  - Audit trails and change tracking
  - Soft deletes and data retention
  - Performance indexes and query optimization
  - Data validation and constraints
  - Backup and recovery strategies
  - Security and encryption (field-level when needed)
  - Compliance features (GDPR, HIPAA, SOX, PCI-DSS)
  - Real-time features when required
  - Analytics and reporting capabilities
  - Integration points for external systems

- **🏗️ Enterprise Architecture**: 
  - Hybrid database architectures
  - Redis caching strategies
  - Elasticsearch search integration
  - Performance monitoring and alerting
  - Horizontal and vertical scaling
  - Multi-region deployment support

- **🔒 Security & Compliance**: 
  - Field-level encryption
  - Role-based access control
  - API rate limiting
  - Compliance frameworks (GDPR, HIPAA, PCI-DSS, SOX)
  - Audit logging and change tracking

- **⚡ Multi-Database Support**: PostgreSQL, DynamoDB
- **☁️ Cloud Deployment**: Automatic AWS deployment (RDS, DynamoDB)
- **📈 Schema Visualization**: ERD diagrams for visual schema review
- **📋 Export Options**: Download SQL scripts, JSON schemas, and connection info

## 🛠 Tech Stack

### Backend
- **FastAPI** (Python) - High-performance async API
- **GPT-5 via OpenAI** - AI agent for requirements gathering
- **Boto3** - AWS infrastructure management
- **PyMongo, SQLAlchemy, psycopg2** - Database drivers

### Frontend
- **React 18** with TypeScript
- **Vite** - Fast build tool and dev server
- **ReactFlow** - Interactive schema visualization
- **TailwindCSS** - Utility-first styling
- **shadcn/ui** - UI component library

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
├── frontend/             # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── api/          # API client
│   │   └── styles/       # CSS
│   ├── package.json      # Dependencies
│   └── index.html
│
└── docs/                 # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 16+ and npm
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

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` (or another port if 5173 is in use).

**Note**: The frontend uses React with TypeScript, Vite, and ReactFlow for the interactive schema visualization. Make sure you have Node.js (v16 or higher) installed.

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
4. **Frontend not loading**: Make sure you've run `npm install` and `npm run dev` in the frontend directory
5. **Node modules missing**: Run `npm install` in the frontend directory

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
