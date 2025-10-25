from typing import Dict, Any

from app.services.deployment.dynamodb import deploy_dynamodb
from app.services.schema_generator import to_dynamodb_defs


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

    # Stubs for future implementations
    if db_type == "postgresql":
        raise NotImplementedError("PostgreSQL deployment not yet implemented")
    if db_type == "mongodb":
        raise NotImplementedError("MongoDB deployment not yet implemented")

    raise ValueError(f"Unsupported db_type: {db_type}")
