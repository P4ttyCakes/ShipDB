# Supabase PostgreSQL Deployment Service

A simple API service to deploy PostgreSQL DDL files to Supabase with automatic Row Level Security (RLS) enablement.

## Features

- ✅ Deploy PostgreSQL schemas to Supabase via REST API
- ✅ Automatic RLS enablement on all tables
- ✅ Multi-table support in single deployment
- ✅ No direct database connection required

## Quick Start

### 1. Prerequisites

Set up your `.env` file in the `backend/` directory:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-key
```

### 2. Create exec_sql Function in Supabase

Run this SQL in your Supabase Dashboard → SQL Editor:

```sql
CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  EXECUTE query;
EXCEPTION WHEN OTHERS THEN
  RAISE EXCEPTION 'SQL execution failed: %', SQLERRM;
END;
$$;

GRANT EXECUTE ON FUNCTION exec_sql(text) TO authenticated;
GRANT EXECUTE ON FUNCTION exec_sql(text) TO anon;
```

### 3. Start the Service

```bash
./start_backend.sh
```

The API will be available at `http://localhost:8000`

## Usage

### Deploy PostgreSQL Schema

```bash
curl -X POST http://localhost:8000/api/postgres \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100)); CREATE TABLE posts (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), title VARCHAR(200));"
  }'
```

### Response

```json
{
  "success": true,
  "message": "Tables created via exec_sql RPC: users, posts",
  "tables_created": ["users", "posts"],
  "method": "exec_sql_rpc",
  "rls_enabled": true
}
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── core/
│   │   │   └── config.py         # Configuration
│   │   └── api/
│   │       └── routes/
│   │           └── deploy.py     # Deployment endpoint
│   ├── claude_supabase_driver.py # Core deployment logic
│   ├── requirements.txt          # Dependencies
│   └── .env                       # Your credentials
├── start_backend.sh               # Start script
└── README.md
```

## How It Works

1. You send PostgreSQL DDL via REST API
2. The service calls Supabase's `exec_sql` RPC function
3. Tables are created in Supabase
4. RLS is automatically enabled on all tables
5. Response confirms deployment and RLS status

## Requirements

- Python 3.12+
- Supabase account
- Active internet connection
