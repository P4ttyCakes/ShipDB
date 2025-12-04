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
                        "method": result.get('method', 'unknown'),
                        "rls_enabled": result.get('rls_enabled', False)
                    },
                    message=f"Successfully deployed to Supabase: {result.get('message', '')}"
                )
            else:
                # Manual execution required - return response with SQL
                return DeploymentResponse(
                    deployment_id=request.project_id,
                    status="pending",
                    database_type="supabase",
                    connection_info={
                        "url": settings.SUPABASE_URL,
                        "tables_created": [],
                        "method": "manual",
                        "sql": result.get('sql', sql_schema),
                        "expected_tables": result.get('expected_tables', []),
                        "instructions": result.get('instructions', '')
                    },
                    message=f"{result.get('message', '')} {result.get('error', '')}"
                )
                
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
                logger.info(f"Attempting direct PostgreSQL connection to execute schema")
                conn = psycopg2.connect(self.db_url)
                cursor = conn.cursor()
                
                # Better SQL statement splitting - handle semicolons properly
                # Split by semicolon, but preserve multi-line statements
                statements = []
                current_statement = []
                for line in table_schema.split('\n'):
                    current_statement.append(line)
                    # Check if line ends with semicolon (not in a string)
                    if line.strip().endswith(';') and not line.strip().startswith('--'):
                        stmt = '\n'.join(current_statement).strip()
                        if stmt:
                            statements.append(stmt)
                        current_statement = []
                
                # Add any remaining statement
                if current_statement:
                    stmt = '\n'.join(current_statement).strip()
                    if stmt:
                        statements.append(stmt)
                
                executed_tables = []
                errors = []
                
                logger.info(f"Executing {len(statements)} SQL statements")
                for i, statement in enumerate(statements):
                    if not statement.strip() or statement.strip().startswith('--'):
                        continue
                    try:
                        logger.debug(f"Executing statement {i+1}/{len(statements)}: {statement[:100]}...")
                        cursor.execute(statement)
                        
                        # Extract table name from CREATE TABLE statements
                        match = re.search(r'CREATE TABLE(?: IF NOT EXISTS)?\s+["\']?(\w+)["\']?', statement, re.IGNORECASE)
                        if match:
                            table_name = match.group(1)
                            executed_tables.append(table_name)
                            logger.info(f"Created table: {table_name}")
                    except Exception as stmt_error:
                        error_msg = f"Statement {i+1} failed: {str(stmt_error)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        # Continue with other statements
                
                if errors:
                    logger.warning(f"Some statements failed: {errors}")
                
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
                
                if executed_tables:
                    logger.info(f"Successfully executed SQL via PostgreSQL connection. Created {len(executed_tables)} tables: {executed_tables}")
                    return {
                        "success": True,
                        "message": f"Successfully created {len(executed_tables)} tables via direct PostgreSQL connection",
                        "tables_created": executed_tables,
                        "method": "psycopg2",
                        "rls_enabled": True,
                        "errors": errors if errors else None
                    }
                else:
                    raise Exception("No tables were created. Check SQL statements for errors.")
            except Exception as pg_error:
                logger.error(f"Direct PostgreSQL connection failed: {pg_error}")
                logger.error(f"Error details: {str(pg_error)}")
        
        # Method 2: Try exec_sql RPC function via Supabase REST API (if custom function exists)
        # Note: This requires a custom RPC function to be created in Supabase
        try:
            logger.info("Attempting to execute SQL via exec_sql RPC function")
            # Call the exec_sql RPC function (if it exists)
            result = self.supabase.rpc('exec_sql', {'query': table_schema}).execute()
            
            # Extract table names from the SQL
            executed_tables = []
            for match in re.finditer(r'CREATE TABLE(?: IF NOT EXISTS)?\s+["\']?(\w+)["\']?', table_schema, re.IGNORECASE):
                executed_tables.append(match.group(1))
            
            logger.info(f"Successfully executed SQL via exec_sql RPC. Tables: {executed_tables}")
            return {
                "success": True,
                "message": f"Tables created via exec_sql RPC",
                "tables_created": executed_tables,
                "method": "exec_sql_rpc",
                "rls_enabled": False  # RLS would need to be enabled separately
            }
        except Exception as rpc_error:
            logger.warning(f"exec_sql RPC failed (this is expected if the function doesn't exist): {rpc_error}")
        
        # Method 3: Fallback - return SQL for manual execution with detailed instructions
        logger.warning("All automatic methods failed. SQL must be executed manually.")
        logger.info(f"Generated SQL schema ({len(table_schema)} characters)")
        
        # Extract table names for user information
        executed_tables = []
        for match in re.finditer(r'CREATE TABLE(?: IF NOT EXISTS)?\s+["\']?(\w+)["\']?', table_schema, re.IGNORECASE):
            executed_tables.append(match.group(1))
        
        return {
            "success": False,
            "message": "Automatic deployment failed. Please execute SQL manually in Supabase Dashboard.",
            "tables_created": [],
            "method": "manual",
            "sql": table_schema,
            "expected_tables": executed_tables,
            "instructions": "To deploy manually:\n1. Go to your Supabase Dashboard\n2. Navigate to SQL Editor\n3. Copy and paste the SQL below\n4. Click 'Run' to execute",
            "error": "SUPABASE_DB_URL not configured or exec_sql RPC function not available. Please configure SUPABASE_DB_URL in your .env file for automatic deployment, or execute the SQL manually."
        }
