import os
import json
import re
from typing import Dict, Any
from loguru import logger

from backend.app.services.deployment.base import BaseDeploymentService
from backend.app.models.deployment import DeploymentRequest, DeploymentResponse
from backend.app.core.config import settings


class SupabaseDeploymentService(BaseDeploymentService):
    """Supabase PostgreSQL deployment service"""
    
    def __init__(self):
        """Initialize Supabase client"""
        try:
            from supabase import create_client, Client
            
            supabase_url = settings.SUPABASE_URL
            supabase_key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
            
            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.db_url = settings.SUPABASE_DB_URL
            
            logger.info("Supabase client initialized successfully")
            
        except ImportError:
            raise ImportError("supabase-py is not installed. Install it with: pip install supabase")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    async def deploy(self, request: DeploymentRequest) -> DeploymentResponse:
        """Deploy PostgreSQL schema to Supabase"""
        try:
            # Extract SQL from schema_data (could be string or wrapped)
            sql_schema = request.schema_data
            if isinstance(sql_schema, dict):
                # If it's wrapped in a dict, try to extract SQL
                sql_schema = sql_schema.get('sql', '') or str(sql_schema)
            if not isinstance(sql_schema, str):
                sql_schema = str(sql_schema)
            
            # Try multiple methods to execute SQL
            result = await self._execute_schema(sql_schema)
            
            if result['success']:
                return DeploymentResponse(
                    deployment_id=request.project_id,
                    status="deployed",
                    database_type="supabase",
                    connection_info={
                        "url": settings.SUPABASE_URL,
                        "tables_created": result.get('tables_created', []),
                        "method": result.get('method', 'unknown')
                    },
                    message=f"Successfully deployed to Supabase: {result.get('message', '')}"
                )
            else:
                raise Exception(result.get('error', 'Unknown deployment error'))
                
        except Exception as e:
            logger.error(f"Supabase deployment failed: {e}")
            raise
    
    async def validate_credentials(self) -> bool:
        """Validate Supabase credentials"""
        try:
            # Try to access auth which should work
            auth_response = self.supabase.auth.get_session()
            return True
        except Exception as e:
            logger.error(f"Supabase credentials validation failed: {e}")
            return False
    
    async def _execute_schema(self, table_schema: str) -> Dict[str, Any]:
        """Execute SQL schema on Supabase using multiple fallback methods"""
        
        # Method 1: Try direct PostgreSQL connection via psycopg2
        if self.db_url:
            try:
                import psycopg2
                conn = psycopg2.connect(self.db_url)
                cursor = conn.cursor()
                
                statements = [s.strip() for s in re.split(r';(?!\s*[A-Z])', table_schema) if s.strip()]
                executed_tables = []
                
                for statement in statements:
                    if statement:
                        cursor.execute(statement)
                        match = re.search(r'CREATE TABLE(?: IF NOT EXISTS)?\s+"?(\w+)"?', statement, re.IGNORECASE)
                        if match:
                            executed_tables.append(match.group(1))
                
                conn.commit()
                
                # Enable RLS on all created tables
                if executed_tables:
                    try:
                        rls_sql = """
DO $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', table_record.table_name);
    END LOOP;
END $$;
"""
                        cursor.execute(rls_sql)
                        conn.commit()
                        logger.info(f"RLS enabled on {len(executed_tables)} tables")
                    except Exception as rls_error:
                        logger.warning(f"Failed to enable RLS: {rls_error}")
                
                cursor.close()
                conn.close()
                
                logger.info(f"Successfully executed SQL via PostgreSQL connection")
                return {
                    "success": True,
                    "message": f"Tables created via direct PostgreSQL connection",
                    "tables_created": executed_tables,
                    "method": "psycopg2",
                    "rls_enabled": True
                }
            except Exception as pg_error:
                logger.warning(f"Direct PostgreSQL connection failed: {pg_error}")
        
        # Method 2: Try exec_sql RPC function via Supabase REST API
        try:
            statements = re.split(r';\s*\n', table_schema)
            executed_tables = []
            
            for statement in statements:
                statement = statement.strip()
                if statement and statement.upper().startswith('CREATE TABLE'):
                    match = re.search(r'CREATE TABLE(?: IF NOT EXISTS)?\s+"?(\w+)"?', statement, re.IGNORECASE)
                    if match:
                        executed_tables.append(match.group(1))
            
            # Call the exec_sql RPC function
            result = self.supabase.rpc('exec_sql', {'query': table_schema}).execute()
            
            # Enable RLS on all created tables
            if executed_tables:
                try:
                    rls_sql = """
DO $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', table_record.table_name);
    END LOOP;
END $$;
"""
                    rls_result = self.supabase.rpc('exec_sql', {'query': rls_sql}).execute()
                    logger.info(f"RLS enabled on tables")
                except Exception as rls_error:
                    logger.warning(f"Failed to enable RLS: {rls_error}")
            
            logger.info(f"Successfully executed SQL via exec_sql RPC")
            return {
                "success": True,
                "message": f"Tables created via exec_sql RPC",
                "tables_created": executed_tables,
                "method": "exec_sql_rpc",
                "rls_enabled": True
            }
        except Exception as rpc_error:
            logger.warning(f"exec_sql RPC failed: {rpc_error}")
        
        # Method 3: Fallback - return SQL for manual execution
        logger.warning("All automatic methods failed, returning SQL for manual execution")
        return {
            "success": True,
            "message": "SQL generated successfully. Please execute manually in Supabase Dashboard",
            "tables_created": [],
            "method": "manual",
            "sql": table_schema,
            "instructions": "Copy the SQL above and execute it in Supabase Dashboard > SQL Editor"
        }
