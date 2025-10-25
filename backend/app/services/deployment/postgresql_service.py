import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.services.deployment.base import BaseDeploymentService
from app.models.deployment import DeploymentRequest, DeploymentResponse
from loguru import logger


class PostgreSQLRDSService(BaseDeploymentService):
    def __init__(self):
        self.rds = boto3.client(
            'rds',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.ec2 = boto3.client('ec2', region_name=settings.AWS_REGION)
    
    async def deploy(self, request: DeploymentRequest) -> DeploymentResponse:
        db_instance_id = f"shipdb-{request.project_id[:8]}"
        
        # 1. Create security group allowing port 5432
        sg_id = await self._create_security_group(db_instance_id)
        
        # 2. Create RDS instance (db.t3.micro for free tier)
        self.rds.create_db_instance(
            DBInstanceIdentifier=db_instance_id,
            DBInstanceClass='db.t3.micro',
            Engine='postgres',
            EngineVersion='15.4',
            MasterUsername=settings.RDS_MASTER_USERNAME,
            MasterPassword=self._generate_password(),
            AllocatedStorage=20,
            VpcSecurityGroupIds=[sg_id],
            PubliclyAccessible=True,
            BackupRetentionPeriod=0  # No backups for hackathon
        )
        
        # 3. Wait for instance to be available (async poll)
        waiter = self.rds.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier=db_instance_id)
        
        # 4. Get endpoint
        response = self.rds.describe_db_instances(
            DBInstanceIdentifier=db_instance_id
        )
        endpoint = response['DBInstances'][0]['Endpoint']['Address']
        
        # 5. Connect and create schema (using psycopg2)
        await self._execute_schema(endpoint, request.schema)
        
        return DeploymentResponse(
            deployment_id=db_instance_id,
            status="deployed",
            database_type="postgresql",
            connection_info={
                "host": endpoint,
                "port": 5432,
                "database": request.database_name,
                "username": settings.RDS_MASTER_USERNAME,
                "password": self._generate_password(),
                "connection_string": f"postgresql://{settings.RDS_MASTER_USERNAME}:password@{endpoint}:5432/{request.database_name}"
            },
            message="PostgreSQL RDS instance deployed successfully"
        )
    
    async def validate_credentials(self) -> bool:
        try:
            self.rds.describe_db_instances()
            return True
        except Exception as e:
            logger.error(f"PostgreSQL RDS credentials validation failed: {e}")
            return False
    
    async def _create_security_group(self, db_instance_id: str) -> str:
        try:
            response = self.ec2.create_security_group(
                GroupName=f"shipdb-{db_instance_id}",
                Description=f"Security group for ShipDB RDS instance {db_instance_id}"
            )
            sg_id = response['GroupId']
            
            # Allow PostgreSQL access from anywhere (hackathon)
            self.ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 5432,
                        'ToPort': 5432,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            return sg_id
        except ClientError as e:
            logger.error(f"Failed to create security group: {e}")
            raise
    
    async def _execute_schema(self, endpoint: str, schema: dict):
        # Placeholder for schema execution
        # Would use psycopg2 to connect and execute SQL
        logger.info(f"Executing schema on {endpoint}")
        pass
    
    def _generate_password(self) -> str:
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(alphabet) for _ in range(16))
