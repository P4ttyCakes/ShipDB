from typing import Dict, Any, List
from loguru import logger
import pymongo
from pymongo import MongoClient
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


def _create_documentdb_instance(aws_config: Dict[str, Any], db_name: str) -> Dict[str, Any]:
    """Create DocumentDB (MongoDB-compatible) instance"""
    try:
        docdb_client = boto3.client(
            'docdb',
            region_name=aws_config.get('region', settings.AWS_REGION),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        
        # Generate unique identifier
        import uuid
        cluster_id = f"shipdb-{db_name}-{str(uuid.uuid4())[:8]}"
        
        # Create DocumentDB cluster
        response = docdb_client.create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine='docdb',
            MasterUsername=aws_config.get('master_username', 'admin'),
            MasterUserPassword=aws_config.get('master_password', 'password123'),
            BackupRetentionPeriod=aws_config.get('backup_retention', 7),
            VpcSecurityGroupIds=aws_config.get('security_groups', []),
            DBSubnetGroupName=aws_config.get('subnet_group'),
            StorageEncrypted=aws_config.get('storage_encrypted', True),
            DeletionProtection=aws_config.get('deletion_protection', False),
            Tags=[
                {'Key': 'Name', 'Value': f'ShipDB-{db_name}'},
                {'Key': 'Project', 'Value': 'ShipDB'},
                {'Key': 'Environment', 'Value': 'development'}
            ]
        )
        
        # Create cluster instance
        instance_response = docdb_client.create_db_instance(
            DBInstanceIdentifier=f"{cluster_id}-instance-1",
            DBInstanceClass=aws_config.get('instance_class', 'db.t3.medium'),
            Engine='docdb',
            DBClusterIdentifier=cluster_id,
            PubliclyAccessible=aws_config.get('publicly_accessible', True),
            Tags=[
                {'Key': 'Name', 'Value': f'ShipDB-{db_name}-instance'},
                {'Key': 'Project', 'Value': 'ShipDB'},
                {'Key': 'Environment', 'Value': 'development'}
            ]
        )
        
        # Wait for cluster to be available
        waiter = docdb_client.get_waiter('db_cluster_available')
        waiter.wait(DBClusterIdentifier=cluster_id)
        
        # Get cluster details
        cluster = docdb_client.describe_db_clusters(DBClusterIdentifier=cluster_id)['DBClusters'][0]
        
        return {
            'cluster_id': cluster_id,
            'endpoint': cluster['Endpoint'],
            'port': cluster['Port'],
            'status': 'available',
            'arn': cluster['DBClusterArn']
        }
        
    except ClientError as e:
        logger.error(f"Failed to create DocumentDB cluster: {e}")
        raise Exception(f"DocumentDB cluster creation failed: {str(e)}")


def _execute_mongo_scripts(connection_string: str, scripts: List[str]) -> bool:
    """Execute MongoDB scripts"""
    try:
        client = MongoClient(connection_string)
        
        for script in scripts:
            if script.strip():
                # Execute each script
                client.admin.command('eval', script)
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to execute MongoDB scripts: {e}")
        return False


def deploy_mongodb(spec: Dict[str, Any], mongo_scripts: List[str], aws_config: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy MongoDB database to AWS DocumentDB"""
    try:
        db_name = spec.get('name', 'shipdb')
        
        # Create DocumentDB cluster
        docdb_info = _create_documentdb_instance(aws_config, db_name)
        
        # Build connection string
        connection_string = (
            f"mongodb://{aws_config.get('master_username', 'admin')}:"
            f"{aws_config.get('master_password', 'password123')}@"
            f"{docdb_info['endpoint']}:{docdb_info['port']}/"
            f"{db_name}?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred"
        )
        
        # Execute MongoDB scripts to create collections and indexes
        success = _execute_mongo_scripts(connection_string, mongo_scripts)
        
        if not success:
            logger.warning("MongoDB scripts execution failed, but DocumentDB cluster was created")
        
        return {
            'status': 'succeeded' if success else 'partial',
            'connection': {
                'service': 'mongodb',
                'host': docdb_info['endpoint'],
                'port': docdb_info['port'],
                'database': db_name,
                'username': aws_config.get('master_username', 'admin'),
                'connection_string': connection_string
            },
            'cluster': docdb_info,
            'notes': 'MongoDB database deployed to AWS DocumentDB. Use the connection string to connect from your application.'
        }
        
    except Exception as e:
        logger.exception("MongoDB deployment failed")
        return {
            'status': 'failed',
            'error': str(e),
            'notes': 'MongoDB deployment failed. Check AWS credentials and permissions.'
        }
