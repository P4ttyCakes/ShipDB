from typing import Dict, Any

from app.services.deployment.dynamodb import deploy_dynamodb
from app.services.deployment.postgresql import deploy_postgresql
from app.services.deployment.mongodb import deploy_mongodb
from app.services.schema_generator import to_dynamodb_defs, to_postgres_sql, to_mongo_scripts


def deploy(db_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    db_type = (db_type or "").lower()
    aws = payload.get("aws") or {}
    artifacts = payload.get("artifacts") or {}
    spec = payload.get("spec") or {}

    if db_type == "dynamodb":
        tables = artifacts.get("dynamodb_tables")
        if not tables and spec:
            # derive from spec if artifacts not provided
            tables = to_dynamodb_defs(spec)
        if not tables:
            raise ValueError("No DynamoDB table definitions provided or derivable from spec")
        return deploy_dynamodb(spec, tables, aws)

    elif db_type == "postgresql":
        sql_script = artifacts.get("postgres_sql")
        if not sql_script and spec:
            # derive from spec if artifacts not provided
            sql_script = to_postgres_sql(spec)
        if not sql_script:
            raise ValueError("No PostgreSQL SQL script provided or derivable from spec")
        return deploy_postgresql(spec, sql_script, aws)

    elif db_type == "mongodb":
        mongo_scripts = artifacts.get("mongo_scripts")
        if not mongo_scripts and spec:
            # derive from spec if artifacts not provided
            mongo_scripts = to_mongo_scripts(spec)
        if not mongo_scripts:
            raise ValueError("No MongoDB scripts provided or derivable from spec")
        return deploy_mongodb(spec, mongo_scripts, aws)

    raise ValueError(f"Unsupported db_type: {db_type}")
