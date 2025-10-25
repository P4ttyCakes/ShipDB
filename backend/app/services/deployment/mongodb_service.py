import httpx
import secrets
import string
import time
import asyncio
from loguru import logger
from app.core.config import settings
from app.services.deployment.base import BaseDeploymentService
from app.models.deployment import DeploymentRequest, DeploymentResponse


class MongoDBAtlasService(BaseDeploymentService):
    def __init__(self):
        self.api_base = "https://cloud.mongodb.com/api/atlas/v1.0"
        self.auth = httpx.DigestAuth(settings.MONGODB_ATLAS_PUBLIC_KEY, 
                                   settings.MONGODB_ATLAS_PRIVATE_KEY)
        self.project_id = settings.MONGODB_ATLAS_PROJECT_ID
    
    async def deploy(self, request: DeploymentRequest) -> DeploymentResponse:
        """Deploy MongoDB database and collections to existing cluster"""
        database_name = request.database_name
        
        try:
            # Connect to existing M0 cluster and create database/collections
            collections_created = await self._create_database_and_collections(
                database_name, request.schema_data
            )
            
            return DeploymentResponse(
                deployment_id=database_name,
                status="deployed",
                database_type="mongodb",
                connection_info={
                    "connection_string": f"mongodb+srv://patlu_db_user:BTZhcCS0utWwUIxG@mult-purpose.vbwbxst.mongodb.net/{database_name}",
                    "username": "patlu_db_user",
                    "password": "BTZhcCS0utWwUIxG",
                    "database": database_name,
                    "cluster_name": "Mult-Purpose",
                    "collections": collections_created
                },
                message=f"Created {len(collections_created)} MongoDB collections"
            )
            
        except Exception as e:
            logger.error(f"Error deploying MongoDB database {database_name}: {e}")
            raise
    
    async def _create_database_and_collections(self, database_name: str, schema_data: dict) -> list:
        """Create database and collections using MongoDB driver (like DynamoDB)"""
        import pymongo
        
        # Connection string for existing M0 cluster
        connection_string = "mongodb+srv://patlu_db_user:BTZhcCS0utWwUIxG@mult-purpose.vbwbxst.mongodb.net/"
        
        collections_created = []
        
        try:
            # Connect to MongoDB
            client = pymongo.MongoClient(connection_string)
            db = client[database_name]
            
            # Handle both formats: simplified and full MongoDB API format (like DynamoDB)
            if isinstance(schema_data, list):
                # Full MongoDB API format (AI's superior format) - like DynamoDB
                logger.info(f"Processing full MongoDB schema with {len(schema_data)} collections")
                
                for collection_def in schema_data:
                    # Update collection name to include database prefix (like DynamoDB)
                    original_collection_name = collection_def.get('collectionName', collection_def.get('name'))
                    collection_name = f"{database_name}_{original_collection_name}"
                    
                    # Create collection
                    collection = db[collection_name]
                    collections_created.append(collection_name)
                    
                    # Create indexes if specified (full MongoDB API format)
                    indexes = collection_def.get('indexes', [])
                    created_indexes = []
                    
                    for index_def in indexes:
                        try:
                            # Handle different index formats
                            if isinstance(index_def, str):
                                # Simple string index
                                collection.create_index(index_def)
                                created_indexes.append(index_def)
                            elif isinstance(index_def, dict):
                                # Full MongoDB index definition
                                keys = index_def.get('keys', [])
                                name = index_def.get('name', f"{'_'.join([k[0] for k in keys])}_idx")
                                unique = index_def.get('unique', False)
                                background = index_def.get('background', True)
                                sparse = index_def.get('sparse', False)
                                
                                collection.create_index(
                                    keys, 
                                    name=name, 
                                    unique=unique, 
                                    background=background,
                                    sparse=sparse
                                )
                                created_indexes.append(name)
                                logger.info(f"Created index {name} on {collection_name}")
                        except Exception as e:
                            logger.warning(f"Failed to create index on {collection_name}: {e}")
                    
                    logger.info(f"Created MongoDB collection: {collection_name} with {len(created_indexes)} indexes")
                    
            else:
                # Simplified format (backward compatibility) - like DynamoDB
                logger.info("Processing simplified schema format")
                
                collections = schema_data.get('collections', [])
                for collection_def in collections:
                    collection_name = f"{database_name}_{collection_def['name']}"
                    
                    # Create collection
                    collection = db[collection_name]
                    collections_created.append(collection_name)
                    
                    # Create basic indexes if specified
                    indexes = collection_def.get('indexes', [])
                    created_indexes = []
                    
                    for index_field in indexes:
                        try:
                            collection.create_index(index_field)
                            created_indexes.append(index_field)
                            logger.info(f"Created index on {index_field} for {collection_name}")
                        except Exception as e:
                            logger.warning(f"Failed to create index on {collection_name}: {e}")
                    
                    logger.info(f"Created MongoDB collection: {collection_name}")
            
            client.close()
            return collections_created
            
        except Exception as e:
            logger.error(f"Error creating database and collections: {e}")
            raise
    
    
    async def validate_credentials(self) -> bool:
        """Validate MongoDB Atlas API credentials"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/groups/{self.project_id}",
                    auth=self.auth,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"MongoDB Atlas credentials validation failed: {e}")
            return False
    
    def _generate_password(self) -> str:
        """Generate a secure password for database user"""
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(alphabet) for _ in range(16))