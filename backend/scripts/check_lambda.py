"""Quick connectivity check: verifies Lambda-RDS-integration is reachable and invokable."""
import json
import sys
import boto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True)) or load_dotenv("backend/.env")

from backend.app.core.config import settings  # noqa: E402

FUNCTION_NAME = "Lambda-RDS-integration"

client = boto3.client(
    "lambda",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

print(f"Checking function: {FUNCTION_NAME} in region {settings.AWS_REGION}")

# 1. Check the function exists
try:
    info = client.get_function(FunctionName=FUNCTION_NAME)
    state = info["Configuration"]["State"]
    runtime = info["Configuration"]["Runtime"]
    print(f"  exists: yes  |  state: {state}  |  runtime: {runtime}")
except client.exceptions.ResourceNotFoundException:
    print("  ERROR: function not found. Check the name and region in your .env.")
    sys.exit(1)

# 2. Invoke it with a ping
print("Invoking with {\"action\": \"ping\"} ...")
response = client.invoke(
    FunctionName=FUNCTION_NAME,
    InvocationType="RequestResponse",
    Payload=json.dumps({"action": "ping"}),
)
status = response["StatusCode"]
payload = json.loads(response["Payload"].read())

if "FunctionError" in response:
    print(f"  ERROR: Lambda returned a function error (HTTP {status})")
    print(f"  payload: {json.dumps(payload, indent=2)}")
    sys.exit(1)

print(f"  HTTP status: {status}")
print(f"  response payload: {json.dumps(payload, indent=2)}")
print("Connection check passed.")
