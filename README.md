# 🚀 ShipDB - Instant Cloud Database Deployment

**ShipDB** is a hackathon MVP that rapidly generates and deploys cloud databases (MongoDB, PostgreSQL, DynamoDB) without manual schema definition or infrastructure management.

## 🏗️ **Project Structure**

```
ShipDB/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Configuration
│   │   ├── models/            # Data models
│   │   ├── services/          # Deployment services
│   │   └── utils/             # Utilities
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/                  # Frontend application
│   └── src/
├── scripts/                   # Demo and test scripts
│   ├── demos/                 # Database demos
│   ├── tests/                 # Test scripts
│   └── run_demos.py          # Demo runner
├── docs/                      # Documentation
└── examples/                  # Usage examples
```

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Configure AWS Credentials**
Create `.env` file in `backend/`:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
OPENAI_API_KEY=your_openai_key
```

### **3. Run Demos**
```bash
# From project root
python scripts/run_demos.py
```

### **4. Start API Server**
```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📊 **Available Demos**

### **Database Generators**
- **E-commerce Database** - Complete online store (12 tables)
- **Social Media Platform** - Full social network (12 tables)
- **AWS Infrastructure Demo** - Show system capabilities

### **Sample Data**
- **E-commerce Sample Data** - Add realistic test data
- **Project Connection Test** - Verify project organization

## 🎯 **Current Projects**

### **🛒 E-commerce Store**
- **Project ID**: `ecommerce_20241025_020803`
- **Database**: `ecommerce_store`
- **Tables**: 12 (users, products, orders, etc.)
- **Status**: ✅ Active with sample data

### **📱 Social Media Platform**
- **Project ID**: `social_media_20251025_023915`
- **Database**: `social_platform`
- **Tables**: 12 (users, posts, comments, etc.)
- **Status**: ✅ Active and ready

## 🔧 **API Endpoints**

### **Deploy Database**
```bash
POST /api/deploy/
{
  "project_id": "my_project",
  "database_type": "dynamodb",
  "database_name": "my_db",
  "schema_data": {
    "tables": [
      {"name": "users", "primary_key": "user_id"},
      {"name": "posts", "primary_key": "post_id"}
    ]
  }
}
```

### **Health Check**
```bash
GET /health
```

## 📚 **Documentation**

- [AWS Infrastructure Complete](docs/AWS_INFRASTRUCTURE_COMPLETE.md)
- [E-commerce Database Guide](docs/ECOMMERCE_DATABASE_COMPLETE.md)
- [Two Projects Overview](docs/TWO_PROJECTS_COMPLETE.md)
- [How to See It in Action](docs/HOW_TO_SEE_IT_IN_ACTION.md)

## 🛠️ **Tech Stack**

- **Backend**: FastAPI (Python)
- **Database**: AWS DynamoDB, MongoDB Atlas, PostgreSQL RDS
- **AI**: OpenAI GPT-4 for schema generation
- **Cloud**: AWS (boto3)
- **Frontend**: Vanilla JavaScript

## 🎯 **Features**

- ✅ **Instant Database Deployment** - Deploy in seconds
- ✅ **AI-Powered Schema Generation** - No manual schema design
- ✅ **Multiple Database Types** - DynamoDB, MongoDB, PostgreSQL
- ✅ **Real AWS Resources** - Production-ready infrastructure
- ✅ **Project Management** - Organized by project IDs
- ✅ **Sample Data** - Ready-to-use test data
- ✅ **REST API** - Easy integration

## 🚀 **Next Steps**

1. **Build Frontend** - Create user interface
2. **Add AI Agent** - Implement schema generation
3. **Enhance Services** - Complete MongoDB/PostgreSQL
4. **Add Features** - Search, analytics, monitoring

## 📞 **Support**

This is a hackathon MVP. For questions or issues, check the documentation in the `docs/` directory.

---

**Built with ❤️ for rapid database deployment** 🚀
