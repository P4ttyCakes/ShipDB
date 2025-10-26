# Supabase PostgreSQL Deployment Integration

## Overview

ShipDB now supports deploying PostgreSQL schemas to Supabase! This integration allows users to deploy their generated database schemas directly to Supabase with a single click.

## Features

- ✅ **Automatic SQL Execution**: Multiple deployment methods with automatic fallback
- ✅ **Table Detection**: Automatically extracts table names from CREATE TABLE statements
- ✅ **Error Handling**: Graceful handling of connection issues
- ✅ **Manual Fallback**: If automatic deployment fails, provides SQL for manual execution
- ✅ **Credential Validation**: Validates Supabase credentials before attempting deployment

## Setup

### 1. Get Supabase Credentials

You need the following from your Supabase project:

1. **Project URL**: `https://your-project.supabase.co`
2. **Anon Key**: Found in Settings > API > anon public
3. **Service Role Key**: Found in Settings > API > service_role secret (use for deployments)
4. **Database URL**: Found in Settings > Database > Connection string

### 2. Configure Environment Variables

Add these to your `.env` file in the `backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGc...  # Your anon key
SUPABASE_SERVICE_KEY=eyJhbGc...  # Your service role key
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Important**: Replace `[PASSWORD]` with your actual database password and `[PROJECT-REF]` with your project reference.

## Usage

### 1. Generate Your Schema

1. Start a conversation with the ShipDB agent
2. Describe your business and database needs
3. Answer the agent's questions
4. Click "Finish & Generate Schema"

### 2. Deploy to Supabase

Once your schema is generated:

1. Look for the **"Deploy to Supabase"** button (purple button)
2. Click the button to deploy your PostgreSQL schema
3. The system will:
   - Extract the PostgreSQL SQL from your generated schema
   - Attempt multiple deployment methods automatically
   - Show you the results

### Deployment Methods

The integration tries these methods in order:

1. **Direct PostgreSQL Connection** (psycopg2)
   - Connects directly to Supabase's PostgreSQL database
   - Executes SQL statements
   - Most reliable method

2. **Supabase REST API** (exec_sql RPC)
   - Uses Supabase's exec_sql remote procedure call
   - Requires exec_sql function to be enabled in Supabase

3. **Manual Execution Fallback**
   - If automatic methods fail, returns the SQL
   - You can copy and execute it in Supabase Dashboard > SQL Editor

## API Endpoints

### Deploy to Supabase

```http
POST /api/projects/deploy-supabase
Content-Type: application/json

{
  "project_id": "your-project-id",
  "database_type": "supabase",
  "database_name": "your-database-name",
  "spec": {
    "postgres_sql": "CREATE TABLE users (...) ...",
    "app_type": "...",
    "entities": [...]
  }
}
```

## Error Handling

### Common Issues

1. **"Invalid Supabase credentials"**
   - Check that your SUPABASE_URL and SUPABASE_KEY are correct
   - Ensure service role key is set if using direct connection

2. **"PostgreSQL schema not found"**
   - Ensure schema generation completed successfully
   - Check that postgres_sql exists in the spec

3. **"Connection failed"**
   - Verify SUPABASE_DB_URL is correct
   - Check that your database password is correct
   - Ensure network connectivity to Supabase

### Fallback Behavior

If automatic deployment fails, the system will:
1. Return the SQL in the response
2. Provide instructions for manual execution
3. Show success message with manual instructions

## Files Modified

### Backend
- `backend/app/core/config.py` - Added Supabase configuration
- `backend/app/models/deployment.py` - Added SUPABASE database type
- `backend/app/services/deployment/supabase_service.py` - New service for Supabase deployment
- `backend/app/services/deployment/factory.py` - Registered Supabase service
- `backend/app/api/routes/projects.py` - Added deploy-supabase endpoint
- `backend/requirements.txt` - Added supabase package
- `backend/env_template.txt` - Added Supabase configuration template

### Frontend
- `frontend/src/pages/Chat.tsx` - Added Supabase deploy button and handler

## Troubleshooting

### Test Supabase Connection

You can verify your Supabase credentials are working by checking the health endpoint:

```bash
curl http://localhost:8000/health
```

### Check Logs

Backend logs will show detailed information about deployment attempts:

```bash
# Check backend logs
tail -f backend/logs/app.log
```

### Manual SQL Execution

If automatic deployment fails, you can manually execute the SQL:

1. Log into Supabase Dashboard
2. Go to SQL Editor
3. Copy the SQL from the deployment response
4. Paste and execute

## Next Steps

- Consider adding deployment status tracking
- Add support for viewing deployed tables
- Implement schema versioning
- Add rollback functionality
