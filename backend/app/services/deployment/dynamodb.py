from typing import Dict, Any, List
from loguru import logger
import botocore
import boto3

from app.core.config import settings


def _ensure_table(client, table_def: Dict[str, Any]) -> Dict[str, Any]:
    name = table_def["TableName"]
    try:
        client.describe_table(TableName=name)
        return {"table": name, "status": "exists"}
    except client.exceptions.ResourceNotFoundException:
        pass
    resp = client.create_table(**table_def)
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=name)
    return {"table": name, "status": "created", "arn": resp["TableDescription"].get("TableArn")}


def deploy_dynamodb(spec: Dict[str, Any], tables_defs: List[Dict[str, Any]], aws: Dict[str, Any]) -> Dict[str, Any]:
    region = (aws or {}).get("region") or settings.AWS_REGION
    client = boto3.client(
        "dynamodb",
        region_name=region,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    results: List[Dict[str, Any]] = []
    for tdef in tables_defs:
        try:
            results.append(_ensure_table(client, tdef))
        except botocore.exceptions.ClientError as e:
            logger.error("Failed to create/ensure table {}: {}", tdef.get("TableName"), e)
            results.append({"table": tdef.get("TableName"), "status": "error", "error": str(e)})
        except Exception as e:
            logger.exception("Unexpected error while deploying table {}", tdef.get("TableName"))
            results.append({"table": tdef.get("TableName"), "status": "error", "error": str(e)})
    status = "succeeded" if all(r.get("status") in ("exists", "created") for r in results) else "partial"
    return {
        "status": status,
        "connection": {"service": "dynamodb", "region": region},
        "tables": results,
        "notes": "Use AWS credentials configured on server to access tables.",
    }
