#!/usr/bin/env python3
"""
Claude-Driven MongoDB Function Service
Functions that Claude can call to manage MongoDB operations
"""

import pymongo
import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from loguru import logger

class ClaudeMongoDBDriver:
    """MongoDB functions that Claude can call"""
    
    def __init__(self):
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Connection string for existing M0 cluster
        self.connection_string = "mongodb+srv://patlu_db_user:BTZhcCS0utWwUIxG@mult-purpose.vbwbxst.mongodb.net/"
        self.client = None  # Lazy initialization
    
    def _get_client(self):
        """Get MongoDB client with lazy initialization"""
        if self.client is None:
            self.client = pymongo.MongoClient(self.connection_string)
        return self.client
    
    def create_collection_simple(self, collection_name: str, indexes: List[str], database_name: str = None) -> Dict[str, Any]:
        """
        Create a simple MongoDB collection with basic indexes
        Claude can call this for basic collection creation
        """
        try:
            # Use proper naming convention - no database prefix for collection names
            db_name = database_name or "claude_db"
            
            client = self._get_client()
            db = client[db_name]
            collection = db[collection_name]  # No prefix - cleaner naming
            
            # Create indexes
            created_indexes = []
            for index_field in indexes:
                try:
                    collection.create_index(index_field)
                    created_indexes.append(index_field)
                    logger.info(f"Created index on {index_field} for {collection_name}")
                except Exception as e:
                    logger.warning(f"Failed to create index on {collection_name}: {e}")
            
            return {
                "success": True,
                "collection_name": collection_name,
                "database": db_name,
                "indexes": created_indexes,
                "message": f"Created collection {collection_name} in database {db_name} with {len(created_indexes)} indexes"
            }
            
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name
            }
    
    def create_collection_advanced(self, collection_schema: Dict[str, Any], database_name: str = None) -> Dict[str, Any]:
        """
        Create MongoDB collection with advanced features (complex indexes, unique constraints)
        Claude can call this for sophisticated collection creation
        """
        try:
            db_name = database_name or "claude_db"
            collection_name = collection_schema.get('collectionName', collection_schema.get('name'))
            
            client = self._get_client()
            db = client[db_name]
            collection = db[collection_name]  # No prefix - cleaner naming
            
            # Create complex indexes
            indexes = collection_schema.get('indexes', [])
            created_indexes = []
            
            for index_def in indexes:
                try:
                    if isinstance(index_def, str):
                        # Simple string index
                        collection.create_index(index_def)
                        created_indexes.append(index_def)
                    elif isinstance(index_def, dict):
                        # Complex index definition
                        keys = index_def.get('keys', [])
                        if not keys:  # Skip empty keys
                            continue
                        name = index_def.get('name', f"{'_'.join([str(k[0]) for k in keys])}_idx")
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
                        logger.info(f"Created advanced index {name} on {collection_name}")
                except Exception as e:
                    logger.warning(f"Failed to create index on {collection_name}: {e}")
            
            return {
                "success": True,
                "collection_name": collection_name,
                "database": db_name,
                "indexes": created_indexes,
                "message": f"Created advanced collection {collection_name} in database {db_name} with {len(created_indexes)} indexes"
            }
            
        except Exception as e:
            logger.error(f"Error creating advanced collection: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_schema.get('collectionName', 'unknown')
            }
    
    def create_index(self, collection_name: str, index_definition: Dict[str, Any], database_name: str = None) -> Dict[str, Any]:
        """
        Create a specific index on an existing collection
        Claude can call this to add indexes to existing collections
        """
        try:
            db_name = database_name or "claude_db"
            full_collection_name = f"{db_name}_{collection_name}"
            
            client = self._get_client()
            db = client[db_name]
            collection = db[full_collection_name]
            
            # Create the index
            keys = index_definition.get('keys', [])
            name = index_definition.get('name', f"{'_'.join([k[0] for k in keys])}_idx")
            unique = index_definition.get('unique', False)
            background = index_definition.get('background', True)
            sparse = index_definition.get('sparse', False)
            
            collection.create_index(
                keys, 
                name=name, 
                unique=unique, 
                background=background,
                sparse=sparse
            )
            
            return {
                "success": True,
                "index_name": name,
                "collection_name": full_collection_name,
                "message": f"Created index {name} on {full_collection_name}"
            }
            
        except Exception as e:
            logger.error(f"Error creating index on {collection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name
            }
    
    def query_collection(self, collection_name: str, query: Dict[str, Any], database_name: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        Query MongoDB collection with filters
        Claude can call this for data retrieval and analytics
        """
        try:
            db_name = database_name or "claude_db"
            full_collection_name = f"{db_name}_{collection_name}"
            
            client = self._get_client()
            db = client[db_name]
            collection = db[full_collection_name]
            
            # Execute query
            results = list(collection.find(query).limit(limit))
            
            return {
                "success": True,
                "collection_name": full_collection_name,
                "results": results,
                "count": len(results),
                "message": f"Found {len(results)} documents in {full_collection_name}"
            }
            
        except Exception as e:
            logger.error(f"Error querying collection {collection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name
            }
    
    def insert_document(self, collection_name: str, document: Dict[str, Any], database_name: str = None) -> Dict[str, Any]:
        """
        Insert a document into MongoDB collection
        Claude can call this for data insertion
        """
        try:
            db_name = database_name or "claude_db"
            full_collection_name = f"{db_name}_{collection_name}"
            
            client = self._get_client()
            db = client[db_name]
            collection = db[full_collection_name]
            
            # Add timestamp
            document['created_at'] = datetime.now().isoformat()
            
            # Insert document
            result = collection.insert_one(document)
            
            return {
                "success": True,
                "document_id": str(result.inserted_id),
                "collection_name": full_collection_name,
                "message": f"Inserted document into {full_collection_name}"
            }
            
        except Exception as e:
            logger.error(f"Error inserting document into {collection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection_name": collection_name
            }
    
    def list_collections(self, database_name: str = None) -> Dict[str, Any]:
        """
        List all collections in a database
        Claude can call this to see what collections exist
        """
        try:
            db_name = database_name or "claude_db"
            client = self._get_client()
            db = client[db_name]
            collections = db.list_collection_names()
            
            return {
                "success": True,
                "database": db_name,
                "collections": collections,
                "count": len(collections),
                "message": f"Found {len(collections)} collections in {db_name}"
            }
            
        except Exception as e:
            logger.error(f"Error listing collections in {database_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "database": database_name
            }
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.client = None

# Global instance
mongodb_driver = ClaudeMongoDBDriver()

# Function registry for Claude
MONGODB_FUNCTION_REGISTRY = {
    "create_collection_simple": mongodb_driver.create_collection_simple,
    "create_collection_advanced": mongodb_driver.create_collection_advanced,
    "create_index": mongodb_driver.create_index,
    "query_collection": mongodb_driver.query_collection,
    "insert_document": mongodb_driver.insert_document,
    "list_collections": mongodb_driver.list_collections,
}

def call_mongodb_function(function_name: str, **kwargs) -> Dict[str, Any]:
    """Call a MongoDB function by name"""
    if function_name in MONGODB_FUNCTION_REGISTRY:
        return MONGODB_FUNCTION_REGISTRY[function_name](**kwargs)
    else:
        return {
            "success": False,
            "error": f"Unknown MongoDB function: {function_name}"
        }
