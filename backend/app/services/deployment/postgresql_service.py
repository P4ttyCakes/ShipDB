import boto3
import psycopg2
from botocore.exceptions import ClientError
try:  # when run from backend/
    from app.core.config import settings
    from app.services.deployment.base import BaseDeploymentService
    from app.models.deployment import DeploymentRequest, DeploymentResponse
except ImportError:  # when run from repo root
    from backend.app.core.config import settings
    from backend.app.services.deployment.base import BaseDeploymentService
    from backend.app.models.deployment import DeploymentRequest, DeploymentResponse
from loguru import logger


class PostgreSQLRDSService(BaseDeploymentService):
    def __init__(self):
        self.rds = boto3.client(
            'rds',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.ec2 = boto3.client(
            'ec2',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    async def deploy(self, request: DeploymentRequest) -> DeploymentResponse:
        db_instance_id = f"shipdb-{request.project_id[:8]}"
        username = settings.RDS_MASTER_USERNAME or 'postgres'
        password = self._generate_password()  # generated once, reused below for both RDS and the connection string

        # 1. Create security group allowing port 5432
        sg_id = await self._create_security_group(db_instance_id)

        # 2. Create RDS instance (db.t3.micro for free tier)
        self.rds.create_db_instance(
            DBInstanceIdentifier=db_instance_id,
            DBInstanceClass='db.t3.micro',
            Engine='postgres',
            EngineVersion='15.4',
            DBName=request.database_name,
            MasterUsername=username,
            MasterPassword=password,
            AllocatedStorage=20,
            VpcSecurityGroupIds=[sg_id],
            # Public by design: ShipDB hands the connection string to the user
            PubliclyAccessible=True,
            StorageEncrypted=True,
            BackupRetentionPeriod=1
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
        await self._execute_schema(endpoint, username, password, request.database_name, request.schema_data)

        connection_string = f"postgresql://{username}:{password}@{endpoint}:5432/{request.database_name}"
        return DeploymentResponse(
            deployment_id=db_instance_id,
            status="deployed",
            database_type="postgresql",
            connection_info={
                "host": endpoint,
                "port": 5432,
                "database": request.database_name,
                "username": username,
                "password": password,
                "connection_string": connection_string
            },
            message="PostgreSQL RDS instance deployed successfully"
        )
    
    async def teardown(self, db_instance_id: str) -> None:
        """Delete the RDS instance and its ShipDB-created security group."""
        response = self.rds.describe_db_instances(DBInstanceIdentifier=db_instance_id)
        instance = response['DBInstances'][0]
        sg_ids = [sg['VpcSecurityGroupId'] for sg in instance.get('VpcSecurityGroups', [])]

        self.rds.delete_db_instance(
            DBInstanceIdentifier=db_instance_id,
            SkipFinalSnapshot=True,
            DeleteAutomatedBackups=True
        )
        # Security groups can't be deleted while the instance still references them
        waiter = self.rds.get_waiter('db_instance_deleted')
        waiter.wait(DBInstanceIdentifier=db_instance_id)
        logger.info(f"Deleted RDS instance: {db_instance_id}")

        for sg_id in sg_ids:
            try:
                sg = self.ec2.describe_security_groups(GroupIds=[sg_id])['SecurityGroups'][0]
                if sg['GroupName'].startswith('shipdb-'):
                    self.ec2.delete_security_group(GroupId=sg_id)
                    logger.info(f"Deleted security group: {sg_id}")
            except ClientError as e:
                logger.warning(f"Could not delete security group {sg_id}: {e}")

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
    
    async def _execute_schema(self, endpoint: str, username: str, password: str, database_name: str, sql_script: str) -> None:
        logger.info(f"Executing schema on {endpoint}")
        conn = psycopg2.connect(
            host=endpoint,
            port=5432,
            dbname=database_name,
            user=username,
            password=password,
        )
        try:
            conn.autocommit = True
            cursor = conn.cursor()
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            for statement in statements:
                cursor.execute(statement)
            cursor.close()
        finally:
            conn.close()
    
    def _generate_password(self) -> str:
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(alphabet) for _ in range(16))




