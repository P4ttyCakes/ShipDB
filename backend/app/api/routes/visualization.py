from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from loguru import logger
from backend.app.core.config import settings

router = APIRouter()


class ChartDBRequest(BaseModel):
    project_id: str
    database_type: str  # "supabase" or "postgresql"


class AnthropicConfig(BaseModel):
    """Return Anthropic API config for ChartDB frontend"""
    anthropic_api_key: str
    anthropic_endpoint: str = "https://api.anthropic.com"
    anthropic_model: str


@router.get("/erd/{project_id}")
async def get_erd(project_id: str):
    """Generate ERD diagram"""
    return {"message": f"ERD for project {project_id} coming soon"}


@router.get("/anthropic-config")
async def get_anthropic_config():
    """Get Anthropic configuration for ChartDB frontend"""
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=400, detail="ANTHROPIC_API_KEY not configured in backend environment")
    
    return AnthropicConfig(
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        anthropic_model=settings.ANTHROPIC_MODEL
    )


class ConvertToChartDBRequest(BaseModel):
    spec: Dict[str, Any]  # The full generated spec from the AI agent


@router.post("/convert-to-chartdb")
async def convert_spec_to_chartdb(request: ConvertToChartDBRequest):
    """Convert ShipDB spec to ChartDB-compatible JSON"""
    try:
        spec = request.spec
        entities = spec.get("entities", [])
        
        if not entities:
            raise HTTPException(status_code=400, detail="No entities found in spec")
        
        # Convert ShipDB entities to ChartDB format
        chartdb_tables = []
        
        for entity in entities:
            entity_name = entity.get("name")
            if not entity_name:
                continue
            
            columns = []
            
            # Process all fields
            for field in entity.get("fields", []):
                field_name = field.get("name")
                field_type = field.get("type", "string")
                
                if not field_name:
                    continue
                
                # Map ShipDB types to PostgreSQL types for ChartDB
                pg_type = _map_to_pg_type(field_type)
                
                column = {
                    "name": field_name,
                    "type": pg_type,
                    "nullable": not field.get("required", False),
                    "primaryKey": field.get("primary_key", False)
                }
                
                columns.append(column)
            
            # Get foreign keys
            foreign_keys = []
            for field in entity.get("fields", []):
                fk_info = field.get("foreign_key")
                if fk_info:
                    fk_column = field.get("name")
                    fk_ref_table = fk_info.get("table")
                    fk_ref_column = fk_info.get("field", "id")
                    
                    if fk_column and fk_ref_table:
                        foreign_keys.append({
                            "columnName": fk_column,
                            "referencedTableName": fk_ref_table,
                            "referencedColumnName": fk_ref_column
                        })
            
            chartdb_tables.append({
                "tableName": entity_name,
                "columns": columns,
                "foreignKeys": foreign_keys
            })
        
        return {"schema": chartdb_tables}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to convert spec to ChartDB format")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


def _map_to_pg_type(shipdb_type: str) -> str:
    """Map ShipDB field types to PostgreSQL types"""
    type_mapping = {
        "string": "text",
        "text": "text",
        "varchar": "text",
        "int": "integer",
        "integer": "integer",
        "bigint": "bigint",
        "smallint": "smallint",
        "float": "double precision",
        "double": "double precision",
        "number": "double precision",
        "decimal": "numeric",
        "numeric": "numeric",
        "bool": "boolean",
        "boolean": "boolean",
        "date": "date",
        "datetime": "timestamp",
        "timestamp": "timestamp",
        "time": "time",
        "json": "jsonb",
        "jsonb": "jsonb",
        "uuid": "uuid",
    }
    return type_mapping.get(shipdb_type.lower(), "text")


@router.post("/sync-from-chartdb")
async def sync_from_chartdb(request: dict):
    """
    Apply changes from ChartDB back to PostgreSQL database
    Expects: { project_id, chartdb_schema, connection_info }
    """
    try:
        project_id = request.get("project_id")
        chartdb_schema = request.get("chartdb_schema")  # The edited ChartDB JSON
        db_url = request.get("connection_info", {}).get("url") or settings.SUPABASE_DB_URL
        
        if not db_url:
            raise HTTPException(status_code=400, detail="Database URL not provided")
        
        # Convert ChartDB schema back to SQL DDL
        sql_migration = _convert_chartdb_to_sql(chartdb_schema)
        
        # Execute the migration
        try:
            import psycopg2
        except ImportError:
            raise HTTPException(status_code=500, detail="psycopg2-binary is not installed")
        
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        try:
            # Execute each statement
            statements = [s.strip() for s in sql_migration.split(';') if s.strip()]
            for statement in statements:
                cursor.execute(statement)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "message": "Schema changes applied successfully",
                "statements_executed": len(statements)
            }
        except psycopg2.Error as exec_error:
            conn.rollback()
            cursor.close()
            conn.close()
            raise HTTPException(status_code=500, detail=f"Failed to apply changes: {str(exec_error)}")
        except Exception as exec_error:
            conn.rollback()
            cursor.close()
            conn.close()
            raise HTTPException(status_code=500, detail=f"Failed to apply changes: {str(exec_error)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to sync from ChartDB")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


def _convert_chartdb_to_sql(chartdb_schema: List[Dict[str, Any]]) -> str:
    """Convert ChartDB schema JSON to PostgreSQL DDL"""
    if not isinstance(chartdb_schema, list):
        raise ValueError("chartdb_schema must be a list of table objects")
    
    statements = []
    
    # Process each table
    for table_data in chartdb_schema:
        if not isinstance(table_data, dict):
            continue
            
        table_name = table_data.get("tableName")
        if not table_name:
            continue
            
        columns = []
        
        for col in table_data.get("columns", []):
            if not isinstance(col, dict):
                continue
                
            col_name = col.get("name")
            col_type = col.get("type")
            nullable = col.get("nullable", True)
            is_pk = col.get("primaryKey", False)
            
            if not col_name or not col_type:
                continue
                
            col_def = f'"{col_name}" {col_type.upper()}'
            
            if not nullable:
                col_def += " NOT NULL"
                
            columns.append(col_def)
        
        # Add primary key constraint if any
        pks = [col["name"] for col in table_data.get("columns", []) if isinstance(col, dict) and col.get("primaryKey")]
        if pks:
            pk_columns = ", ".join([f'"{pk}"' for pk in pks])
            pk_def = f'PRIMARY KEY ({pk_columns})'
            columns.append(pk_def)
        
        # Add foreign keys
        for fk in table_data.get("foreignKeys", []):
            if not isinstance(fk, dict):
                continue
            fk_def = (f'FOREIGN KEY ("{fk["columnName"]}") '
                      f'REFERENCES "{fk["referencedTableName"]}"("{fk["referencedColumnName"]}")')
            columns.append(fk_def)
        
        if columns:
            create_table = f'''CREATE TABLE IF NOT EXISTS "{table_name}" ({', '.join(columns)});'''
            statements.append(create_table)
    
    return "\n".join(statements)
