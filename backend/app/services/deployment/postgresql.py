from typing import Dict, Any, List
from loguru import logger
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import boto3
from botocore.exceptions import ClientError

from backend.app.core.config import settings


def _create_rds_instance(aws_config: Dict[str, Any], db_name: str) -> Dict[str, Any]:
    """Create RDS PostgreSQL instance"""
    try:
        rds_client = boto3.client(
            'rds',
            region_name=aws_config.get('region', settings.AWS_REGION),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        
        # Generate unique identifier
        import uuid
        instance_id = f"shipdb-{db_name}-{str(uuid.uuid4())[:8]}"
        
        # Create RDS instance
        response = rds_client.create_db_instance(
            DBInstanceIdentifier=instance_id,
            DBInstanceClass=aws_config.get('instance_class', 'db.t3.micro'),
            Engine='postgres',
            EngineVersion=aws_config.get('engine_version', '15.4'),
            MasterUsername=aws_config.get('master_username', 'postgres'),
            MasterUserPassword=aws_config.get('master_password', 'password123'),
            AllocatedStorage=aws_config.get('allocated_storage', 20),
            StorageType=aws_config.get('storage_type', 'gp2'),
            VpcSecurityGroupIds=aws_config.get('security_groups', []),
            DBSubnetGroupName=aws_config.get('subnet_group'),
            BackupRetentionPeriod=aws_config.get('backup_retention', 7),
            MultiAZ=aws_config.get('multi_az', False),
            PubliclyAccessible=aws_config.get('publicly_accessible', True),
            StorageEncrypted=aws_config.get('storage_encrypted', True),
            DeletionProtection=aws_config.get('deletion_protection', False),
            Tags=[
                {'Key': 'Name', 'Value': f'ShipDB-{db_name}'},
                {'Key': 'Project', 'Value': 'ShipDB'},
                {'Key': 'Environment', 'Value': 'development'}
            ]
        )
        
        # Wait for instance to be available
        waiter = rds_client.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier=instance_id)
        
        # Get instance details
        instance = rds_client.describe_db_instances(DBInstanceIdentifier=instance_id)['DBInstances'][0]
        
        return {
            'instance_id': instance_id,
            'endpoint': instance['Endpoint']['Address'],
            'port': instance['Endpoint']['Port'],
            'status': 'available',
            'arn': instance['DBInstanceArn']
        }
        
    except ClientError as e:
        logger.error(f"Failed to create RDS instance: {e}")
        raise Exception(f"RDS instance creation failed: {str(e)}")


def _execute_sql_script(connection_string: str, sql_script: str) -> bool:
    """Execute SQL script on PostgreSQL database"""
    try:
        conn = psycopg2.connect(connection_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Split script into individual statements
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to execute SQL script: {e}")
        return False


def deploy_postgresql(spec: Dict[str, Any], sql_script: str, aws_config: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy PostgreSQL database to AWS RDS"""
    try:
        db_name = spec.get('name', 'shipdb')
        
        # Create RDS instance
        rds_info = _create_rds_instance(aws_config, db_name)
        
        # Build connection string
        connection_string = (
            f"postgresql://{aws_config.get('master_username', 'postgres')}:"
            f"{aws_config.get('master_password', 'password123')}@"
            f"{rds_info['endpoint']}:{rds_info['port']}/"
            f"{db_name}"
        )
        
        # Execute SQL script to create tables
        success = _execute_sql_script(connection_string, sql_script)
        
        if not success:
            logger.warning("SQL script execution failed, but RDS instance was created")
        
        return {
            'status': 'succeeded' if success else 'partial',
            'connection': {
                'service': 'postgresql',
                'host': rds_info['endpoint'],
                'port': rds_info['port'],
                'database': db_name,
                'username': aws_config.get('master_username', 'postgres'),
                'connection_string': connection_string
            },
            'instance': rds_info,
            'notes': 'PostgreSQL database deployed to AWS RDS. Use the connection string to connect from your application.'
        }
        
    except Exception as e:
        logger.exception("PostgreSQL deployment failed")
        return {
            'status': 'failed',
            'error': str(e),
            'notes': 'PostgreSQL deployment failed. Check AWS credentials and permissions.'
        }
