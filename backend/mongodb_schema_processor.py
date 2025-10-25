#!/usr/bin/env python3
"""
MongoDB Schema Processor
Converts JSON schema files to MongoDB collections and uploads to cluster
"""

import json
import pymongo
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

class MongoDBSchemaProcessor:
    """Processes JSON schemas and creates MongoDB collections"""
    
    def __init__(self):
        load_dotenv()
        # Connection string for existing M0 cluster
        self.connection_string = "mongodb+srv://patlu_db_user:BTZhcCS0utWwUIxG@mult-purpose.vbwbxst.mongodb.net/"
        self.client = None
    
    def _get_client(self):
        """Get MongoDB client with lazy initialization"""
        if self.client is None:
            self.client = pymongo.MongoClient(self.connection_string)
        return self.client
    
    def process_json_schema(self, schema_data: Dict[str, Any], database_name: str = "schema_db") -> Dict[str, Any]:
        """
        Process JSON schema and create MongoDB collections
        
        Args:
            schema_data: JSON schema with definitions
            database_name: Target database name
            
        Returns:
            Dict with creation results
        """
        try:
            client = self._get_client()
            db = client[database_name]
            
            results = {
                "success": True,
                "database": database_name,
                "collections_created": [],
                "errors": []
            }
            
            # Process each definition in the schema
            definitions = schema_data.get("definitions", {})
            
            for collection_name, schema_def in definitions.items():
                try:
                    collection_result = self._create_collection_from_schema(
                        db, collection_name, schema_def
                    )
                    results["collections_created"].append(collection_result)
                    logger.info(f"Created collection {collection_name} with {len(collection_result['indexes'])} indexes")
                    
                except Exception as e:
                    error_msg = f"Failed to create collection {collection_name}: {e}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing schema: {e}")
            return {
                "success": False,
                "error": str(e),
                "database": database_name,
                "collections_created": [],
                "errors": []
            }
    
    def _create_collection_from_schema(self, db, collection_name: str, schema_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a MongoDB collection from a JSON schema definition
        
        Args:
            db: MongoDB database object
            collection_name: Name of the collection
            schema_def: JSON schema definition for the collection
            
        Returns:
            Dict with collection creation details
        """
        collection = db[collection_name]
        
        # Extract properties and required fields
        properties = schema_def.get("properties", {})
        required_fields = schema_def.get("required", [])
        
        # Create indexes based on schema
        indexes_created = []
        
        # 1. Create unique index on required fields that look like IDs
        for field in required_fields:
            if field in ["id", "user_id", "product_id", "order_id"] or field.endswith("_id"):
                try:
                    collection.create_index(field, unique=True)
                    indexes_created.append(f"{field}_unique")
                    logger.info(f"Created unique index on {field}")
                except Exception as e:
                    logger.warning(f"Failed to create unique index on {field}: {e}")
        
        # 2. Create indexes on common query fields
        common_index_fields = ["name", "email", "username", "created_at", "updated_at", "status", "type"]
        for field in common_index_fields:
            if field in properties:
                try:
                    collection.create_index(field)
                    indexes_created.append(field)
                    logger.info(f"Created index on {field}")
                except Exception as e:
                    logger.warning(f"Failed to create index on {field}: {e}")
        
        # 3. Create compound indexes for common query patterns
        compound_indexes = self._generate_compound_indexes(properties, required_fields)
        for compound_index in compound_indexes:
            try:
                collection.create_index(compound_index["keys"], name=compound_index["name"])
                indexes_created.append(compound_index["name"])
                logger.info(f"Created compound index: {compound_index['name']}")
            except Exception as e:
                logger.warning(f"Failed to create compound index {compound_index['name']}: {e}")
        
        # 4. Create text index for searchable fields
        text_fields = []
        for field, field_def in properties.items():
            if field_def.get("type") == "string" and field in ["name", "title", "description", "content"]:
                text_fields.append(field)
        
        if text_fields:
            try:
                text_index = [(field, "text") for field in text_fields]
                collection.create_index(text_index, name="text_search")
                indexes_created.append("text_search")
                logger.info(f"Created text search index on: {text_fields}")
            except Exception as e:
                logger.warning(f"Failed to create text index: {e}")
        
        return {
            "collection_name": collection_name,
            "indexes": indexes_created,
            "properties": list(properties.keys()),
            "required_fields": required_fields,
            "schema": schema_def
        }
    
    def _generate_compound_indexes(self, properties: Dict[str, Any], required_fields: List[str]) -> List[Dict[str, Any]]:
        """
        Generate compound indexes based on schema analysis
        
        Args:
            properties: Schema properties
            required_fields: Required fields from schema
            
        Returns:
            List of compound index definitions
        """
        compound_indexes = []
        
        # Common compound index patterns
        patterns = [
            # User-related patterns
            (["user_id", "created_at"], "user_timeline"),
            (["user_id", "status"], "user_status"),
            
            # Product-related patterns
            (["type", "price"], "type_price"),
            (["type", "inventory_count"], "type_inventory"),
            (["created_at", "type"], "timeline_type"),
            
            # General patterns
            (["status", "created_at"], "status_timeline"),
            (["type", "status"], "type_status"),
        ]
        
        for fields, name in patterns:
            if all(field in properties for field in fields):
                compound_indexes.append({
                    "keys": [(field, 1) for field in fields],
                    "name": name
                })
        
        return compound_indexes
    
    def process_schema_file(self, file_path: str, database_name: str = "schema_db") -> Dict[str, Any]:
        """
        Process a JSON schema file and create MongoDB collections
        
        Args:
            file_path: Path to JSON schema file
            database_name: Target database name
            
        Returns:
            Dict with creation results
        """
        try:
            with open(file_path, 'r') as f:
                schema_data = json.load(f)
            
            return self.process_json_schema(schema_data, database_name)
            
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Schema file not found: {file_path}",
                "database": database_name
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in schema file: {e}",
                "database": database_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing schema file: {e}",
                "database": database_name
            }
    
    def list_collections(self, database_name: str = "schema_db") -> Dict[str, Any]:
        """List all collections in a database"""
        try:
            client = self._get_client()
            db = client[database_name]
            collections = db.list_collection_names()
            
            collection_details = []
            for collection_name in collections:
                collection = db[collection_name]
                indexes = list(collection.list_indexes())
                collection_details.append({
                    "name": collection_name,
                    "indexes": [idx["name"] for idx in indexes],
                    "index_count": len(indexes)
                })
            
            return {
                "success": True,
                "database": database_name,
                "collections": collection_details,
                "total_collections": len(collections)
            }
            
        except Exception as e:
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
schema_processor = MongoDBSchemaProcessor()

def process_schema_file(file_path: str, database_name: str = "schema_db") -> Dict[str, Any]:
    """Process a JSON schema file and create MongoDB collections"""
    return schema_processor.process_schema_file(file_path, database_name)

def process_schema_data(schema_data: Dict[str, Any], database_name: str = "schema_db") -> Dict[str, Any]:
    """Process JSON schema data and create MongoDB collections"""
    return schema_processor.process_json_schema(schema_data, database_name)

def list_database_collections(database_name: str = "schema_db") -> Dict[str, Any]:
    """List all collections in a database"""
    return schema_processor.list_collections(database_name)

# Example usage
if __name__ == "__main__":
    # Example schema data
    example_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {
            "products": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "price": {"type": "string"},
                    "inventory_count": {"type": "integer"},
                    "created_at": {"type": "string"}
                },
                "required": ["id", "name", "type", "price", "inventory_count", "created_at"]
            }
        }
    }
    
    # Process the schema
    result = process_schema_data(example_schema, "ecommerce")
    print("Schema processing result:", result)
    
    # List collections
    collections = list_database_collections("ecommerce")
    print("Collections:", collections)
