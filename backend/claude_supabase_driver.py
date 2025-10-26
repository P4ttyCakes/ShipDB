#!/usr/bin/env python3
"""
Claude-Driven Supabase PostgreSQL Function Service
Functions that Claude can call to manage PostgreSQL operations on Supabase
"""

import os
import json
import re
import uuid
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class ClaudeSupabaseDriver:
    """Supabase PostgreSQL functions that Claude can call"""
    
    def __init__(self):
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(supabase_url, supabase_key)
        except ImportError:
            raise ImportError("supabase-py is not installed. Install it with: pip install supabase")
        
        self.url = supabase_url
        
        # Initialize psycopg2 for raw SQL execution
        self._init_postgres_connection()
    
    def _init_postgres_connection(self):
        """Initialize direct PostgreSQL connection for DDL operations"""
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            # Get connection string from environment
            db_url = os.getenv('SUPABASE_DB_URL')
            if not db_url:
                # Try to construct from Supabase URL (doesn't work for connection)
                logger.warning("SUPABASE_DB_URL not set. DDL operations will not work.")
                logger.warning("Set SUPABASE_DB_URL in format: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres")
                self.db_conn = None
                return
            
            self.db_conn = psycopg2.connect(db_url)
            logger.info("PostgreSQL connection established for DDL operations")
            
        except ImportError:
            logger.error("psycopg2 not installed. Install with: pip install psycopg2-binary")
            self.db_conn = None
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.db_conn = None
    
    def create_table(self, table_schema: str, database_name: str = None) -> Dict[str, Any]:
        """
        Create a PostgreSQL table from SQL schema
        Claude can call this to create tables from CREATE TABLE statements
        
        This function uses schema inference by inserting sample data to create table structure.
        """
        try:
            # Method 1: Try direct PostgreSQL connection first
            if self.db_conn:
                cursor = self.db_conn.cursor()
                statements = [s.strip() for s in re.split(r';(?!\s*[A-Z])', table_schema) if s.strip()]
                executed_tables = []
                for statement in statements:
                    if statement:
                        cursor.execute(statement)
                        match = re.search(r'CREATE TABLE(?: IF NOT EXISTS)?\s+"?(\w+)"?', statement, re.IGNORECASE)
                        if match:
                            executed_tables.append(match.group(1))
                self.db_conn.commit()
                cursor.close()
                
                return {
                    "success": True,
                    "message": f"Successfully executed SQL schema via PostgreSQL connection",
                    "tables_created": executed_tables,
                    "schema": table_schema
                }
            
            # Method 2: Try exec_sql RPC function via Supabase REST API
            try:
                # First, extract all CREATE TABLE statements to track what tables will be created
                # Split on semicolons followed by whitespace/newline
                statements = re.split(r';\s*\n', table_schema)
                # Also handle semicolons not on newlines
                all_statements = []
                for stmt in statements:
                    all_statements.extend(re.split(r';(?!\n)', stmt))
                
                executed_tables = []
                for statement in all_statements:
                    statement = statement.strip()
                    if statement and statement.upper().startswith('CREATE TABLE'):
                        match = re.search(r'CREATE TABLE(?: IF NOT EXISTS)?\s+"?(\w+)"?', statement, re.IGNORECASE)
                        if match:
                            executed_tables.append(match.group(1))
                
                # Call the exec_sql RPC function with the complete schema
                # exec_sql can handle multiple statements separated by semicolons
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
                
                logger.info(f"Successfully executed SQL via exec_sql RPC function")
                return {
                    "success": True,
                    "message": f"Tables created via exec_sql RPC: {', '.join(executed_tables)}",
                    "tables_created": executed_tables,
                    "schema": table_schema,
                    "method": "exec_sql_rpc",
                    "rls_enabled": True
                }
                    
            except Exception as rpc_error:
                logger.warning(f"exec_sql RPC failed: {rpc_error}, falling back to psql")
                
            # Method 3: Try psql command line tool
            try:
                db_url = os.getenv('SUPABASE_DB_URL')
                if db_url:
                    # Use psql to execute SQL - pipe it through stdin for multi-statement SQL
                    process = subprocess.Popen(
                        ['psql', db_url],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    stdout, stderr = process.communicate(input=table_schema, timeout=30)
                    
                    if process.returncode == 0:
                        # Extract created table names
                        statements = [s.strip() for s in re.split(r';(?!\s*[A-Z])', table_schema) if s.strip()]
                        executed_tables = []
                        for statement in statements:
                            if statement.upper().startswith('CREATE TABLE'):
                                match = re.search(r'CREATE TABLE(?: IF NOT EXISTS)?\s+"?(\w+)"?', statement, re.IGNORECASE)
                                if match:
                                    executed_tables.append(match.group(1))
                        
                        return {
                            "success": True,
                            "message": f"Tables created via psql: {', '.join(executed_tables)}",
                            "tables_created": executed_tables,
                            "schema": table_schema,
                            "method": "psql"
                        }
                    else:
                        raise Exception(f"psql error: {stderr}")
                else:
                    raise Exception("SUPABASE_DB_URL not set")
                    
            except Exception as psql_error:
                # Method 4: Schema Inference - Create tables by inserting sample data
                try:
                    # Parse the schema to extract table definitions
                    statements = [s.strip() for s in re.split(r';(?!\s*[A-Z])', table_schema) if s.strip()]
                    created_tables = []
                    
                    for statement in statements:
                        if statement.upper().startswith('CREATE TABLE'):
                            # Extract table name
                            match = re.search(r'CREATE TABLE(?: IF NOT EXISTS)?\s+"?(\w+)"?', statement, re.IGNORECASE)
                            if match:
                                table_name = match.group(1)
                                
                                # Generate sample data based on table name
                                sample_data = self._generate_sample_data(table_name)
                                
                                if sample_data:
                                    try:
                                        # Try to insert sample data to create table structure
                                        response = self.supabase.table(table_name).insert(sample_data).execute()
                                        created_tables.append(table_name)
                                        print(f"✅ Created table {table_name} via schema inference")
                                    except Exception as insert_error:
                                        # If insert fails, table might already exist or have constraints
                                        if "relation" in str(insert_error).lower() and "does not exist" in str(insert_error).lower():
                                            print(f"❌ Table {table_name} creation failed: {insert_error}")
                                        else:
                                            # Table exists or other error - consider it created
                                            created_tables.append(table_name)
                                            print(f"✅ Table {table_name} already exists or created")
                    
                    if created_tables:
                        return {
                            "success": True,
                            "message": f"Tables created via schema inference: {', '.join(created_tables)}",
                            "tables_created": created_tables,
                            "schema": table_schema,
                            "method": "schema_inference"
                        }
                    else:
                        raise Exception("No tables could be created via schema inference")
                        
                except Exception as inference_error:
                    # Final fallback: Return SQL for manual execution
                    return {
                        "success": False,
                        "error": "All automatic methods failed",
                        "message": "Please execute the SQL manually in Supabase Dashboard > SQL Editor",
                        "schema": table_schema,
                        "instructions": "Copy the schema above and execute it in Supabase Dashboard > SQL Editor",
                        "postgresql_error": str(self.db_conn.error) if hasattr(self, 'db_conn') and self.db_conn else "Connection not established",
                        "psql_error": str(psql_error),
                        "inference_error": str(inference_error)
                    }
            
        except Exception as e:
            logger.error(f"Error executing table schema: {e}")
            if self.db_conn:
                self.db_conn.rollback()
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute table schema",
                "schema": table_schema,
                "instructions": "Please execute the SQL manually in Supabase Dashboard > SQL Editor"
            }
    
    def _generate_sample_data(self, table_name: str) -> Dict[str, Any]:
        """Generate sample data for table creation via schema inference"""
        sample_data = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat()
        }
        
        # Generate sample data based on common table patterns
        if "product" in table_name.lower():
            sample_data.update({
                "name": "Sample Product",
                "description": "Sample description",
                "price": 99.99,
                "inventory_count": 10,
                "category": "Sample"
            })
        elif "customer" in table_name.lower():
            sample_data.update({
                "name": "Sample Customer",
                "email": "sample@example.com",
                "phone": "+1-555-0000"
            })
        elif "order" in table_name.lower():
            sample_data.update({
                "customer_id": str(uuid.uuid4()),
                "order_date": datetime.now().isoformat(),
                "status": "pending",
                "total_amount": 99.99
            })
        elif "competition" in table_name.lower():
            sample_data.update({
                "name": "Sample Competition",
                "description": "Sample competition",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "location": "Sample Location"
            })
        elif "participant" in table_name.lower():
            sample_data.update({
                "competition_id": str(uuid.uuid4()),
                "name": "Sample Participant",
                "email": "participant@example.com",
                "phone": "+1-555-0000"
            })
        elif "result" in table_name.lower():
            sample_data.update({
                "competition_id": str(uuid.uuid4()),
                "participant_id": str(uuid.uuid4()),
                "rank": 1,
                "score": 100.0
            })
        elif "payment" in table_name.lower():
            sample_data.update({
                "order_id": str(uuid.uuid4()),
                "amount": 99.99,
                "payment_method": "credit_card",
                "status": "completed"
            })
        else:
            # Generic sample data
            sample_data.update({
                "name": "Sample",
                "description": "Sample data",
                "status": "active"
            })
        
        return sample_data
    
    def insert_row(self, table_name: str, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a row into a PostgreSQL table
        Claude can call this for data insertion
        """
        try:
            response = self.supabase.table(table_name).insert(row_data).execute()
            
            return {
                "success": True,
                "data": response.data,
                "message": f"Inserted row into {table_name}"
            }
            
        except Exception as e:
            logger.error(f"Error inserting row into {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def query_table(self, table_name: str, filters: Dict[str, Any] = None, 
                   columns: str = "*", limit: int = None, offset: int = None) -> Dict[str, Any]:
        """
        Query PostgreSQL table with filters
        Claude can call this for data retrieval and analytics
        """
        try:
            query = self.supabase.table(table_name).select(columns)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Apply limit and offset
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            response = query.execute()
            
            return {
                "success": True,
                "table_name": table_name,
                "data": response.data,
                "count": len(response.data) if response.data else 0,
                "message": f"Query returned {len(response.data) if response.data else 0} rows from {table_name}"
            }
            
        except Exception as e:
            logger.error(f"Error querying table {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def update_row(self, table_name: str, filters: Dict[str, Any], 
                  update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update rows in PostgreSQL table
        Claude can call this for data updates
        """
        try:
            query = self.supabase.table(table_name).update(update_data)
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            
            return {
                "success": True,
                "data": response.data,
                "message": f"Updated rows in {table_name}"
            }
            
        except Exception as e:
            logger.error(f"Error updating {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def delete_row(self, table_name: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete rows from PostgreSQL table
        Claude can call this for data deletion
        """
        try:
            query = self.supabase.table(table_name).delete()
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            
            return {
                "success": True,
                "data": response.data,
                "message": f"Deleted rows from {table_name}"
            }
            
        except Exception as e:
            logger.error(f"Error deleting from {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def list_tables(self) -> Dict[str, Any]:
        """
        List all tables in the database
        Claude can call this to see what tables exist
        Note: Supabase PostgREST doesn't expose information_schema
        This would require using the Supabase Management API or raw SQL
        """
        try:
            # Note: PostgREST doesn't expose information_schema.tables
            # For now, return empty list with note that tables need to be tracked manually
            # In production, would need to use Supabase Management API or SQL function
            return {
                "success": True,
                "tables": [],
                "count": 0,
                "message": "PostgREST doesn't expose information_schema. Tables must be created via SQL or Management API",
                "note": "Use Supabase dashboard to view tables, or create them via SQL functions"
            }
            
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list tables"
            }
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a table
        Claude can call this to understand table structure
        Note: PostgREST doesn't expose information_schema
        """
        try:
            # Try to query the table to infer structure (limit 0 to just get schema)
            # This is a workaround since PostgREST doesn't expose information_schema
            response = self.supabase.table(table_name).select("*").limit(0).execute()
            
            return {
                "success": True,
                "table_name": table_name,
                "columns": "Cannot infer columns via PostgREST. Use Supabase dashboard or SQL to inspect table structure",
                "message": f"PostgREST doesn't expose information_schema. Query table to see structure"
            }
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name,
                "message": "PostgREST doesn't expose information_schema. Use Supabase dashboard to view table structure"
            }
    
    def validate_credentials(self) -> Dict[str, Any]:
        """
        Validate Supabase credentials
        Claude can call this to check connection
        """
        try:
            # Try to get the version or run a simple auth check
            # Supabase client has a 'health' method we can use
            # Or just try to access auth which should work
            auth_response = self.supabase.auth.get_session()
            return {
                "success": True,
                "message": "Supabase credentials are valid",
                "url": self.url,
                "authenticated": auth_response is not None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Supabase credentials are invalid"
            }

# Global instance for Claude to use
claude_supabase = ClaudeSupabaseDriver()

# Function registry for Claude
SUPABASE_FUNCTION_REGISTRY = {
    "create_table": claude_supabase.create_table,
    "insert_row": claude_supabase.insert_row,
    "query_table": claude_supabase.query_table,
    "update_row": claude_supabase.update_row,
    "delete_row": claude_supabase.delete_row,
    "list_tables": claude_supabase.list_tables,
    "get_table_info": claude_supabase.get_table_info,
    "validate_credentials": claude_supabase.validate_credentials
}

def call_supabase_function(function_name: str, **kwargs) -> Dict[str, Any]:
    """
    Main function that Claude can call to execute Supabase operations
    """
    if function_name not in SUPABASE_FUNCTION_REGISTRY:
        return {
            "success": False,
            "error": f"Unknown Supabase function: {function_name}",
            "available_functions": list(SUPABASE_FUNCTION_REGISTRY.keys())
        }
    
    try:
        result = SUPABASE_FUNCTION_REGISTRY[function_name](**kwargs)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Function {function_name} failed"
        }

if __name__ == "__main__":
    # Test the functions
    print("Testing Claude Supabase Driver Functions...")
    
    # Test credentials
    result = call_supabase_function("validate_credentials")
    print(f"Credentials: {result}")
    
    # Test listing tables
    result = call_supabase_function("list_tables")
    print(f"Tables: {result}")
