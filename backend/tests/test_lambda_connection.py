import json
import boto3
import pytest
from backend.app.core.config import settings

FUNCTION_NAME = "Lambda-RDS-integration"


@pytest.fixture(scope="module")
def lambda_client():
    return boto3.client(
        "lambda",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def test_lambda_function_exists(lambda_client):
    """Confirm the function is deployed and reachable."""
    response = lambda_client.get_function(FunctionName=FUNCTION_NAME)
    assert response["Configuration"]["FunctionName"] == FUNCTION_NAME
    assert response["Configuration"]["State"] == "Active"


def test_lambda_invoke_ping(lambda_client):
    """Invoke the function with a ping payload and expect a 200 status code back."""
    response = lambda_client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({"action": "ping"}),
    )
    assert response["StatusCode"] == 200

    # If the function returns a body, check it didn't error
    payload = json.loads(response["Payload"].read())
    assert "FunctionError" not in response, f"Lambda returned an error: {payload}"
