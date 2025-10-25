#!/usr/bin/env python3
"""
Intelligent AI Agent for ShipDB - Truly Adaptive Database Generation
This replaces the hardcoded templates with intelligent analysis
"""

import re
from typing import Dict, Any, List

class IntelligentAIAgent:
    """Truly intelligent AI agent that analyzes user requirements and generates custom databases."""
    
    def analyze_business_requirements(self, conversation_text: str) -> Dict[str, Any]:
        """Analyze conversation text to extract business requirements intelligently."""
        text_lower = conversation_text.lower()
        
        # Extract business domain
        domain = self._extract_business_domain(text_lower)
        
        # Extract scale indicators
        scale = self._extract_scale_indicators(text_lower)
        
        # Extract required features
        features = self._extract_required_features(text_lower)
        
        # Extract compliance requirements
        compliance = self._extract_compliance_requirements(text_lower)
        
        # Extract technical requirements
        technical = self._extract_technical_requirements(text_lower)
        
        return {
            "domain": domain,
            "scale": scale,
            "features": features,
            "compliance": compliance,
            "technical": technical,
            "conversation_text": conversation_text
        }

    def _extract_business_domain(self, text: str) -> Dict[str, Any]:
        """Extract business domain and key entities from conversation."""
        domain_info = {
            "primary_domain": "general",
            "subdomains": [],
            "key_entities": [],
            "business_model": "unknown",
            "target_users": []
        }
        
        # Healthcare domain
        if any(word in text for word in ["healthcare", "medical", "patient", "hospital", "clinic", "doctor", "nurse", "treatment", "diagnosis", "hipaa"]):
            domain_info["primary_domain"] = "healthcare"
            domain_info["subdomains"].extend(["patient_management", "medical_records", "appointments", "prescriptions"])
            domain_info["key_entities"].extend(["patients", "doctors", "appointments", "medical_records", "prescriptions", "treatments"])
            domain_info["target_users"].extend(["patients", "healthcare_providers", "administrators"])
        
        # E-commerce domain
        elif any(word in text for word in ["ecommerce", "e-commerce", "store", "shop", "product", "inventory", "order", "payment", "cart", "customer"]):
            domain_info["primary_domain"] = "ecommerce"
            domain_info["subdomains"].extend(["product_catalog", "order_management", "payment_processing", "inventory_management"])
            domain_info["key_entities"].extend(["products", "customers", "orders", "payments", "inventory", "categories", "reviews"])
            domain_info["business_model"] = "b2c"
            domain_info["target_users"].extend(["customers", "sellers", "administrators"])
        
        # SaaS domain
        elif any(word in text for word in ["saas", "software", "platform", "service", "subscription", "tenant", "multi-tenant", "api"]):
            domain_info["primary_domain"] = "saas"
            domain_info["subdomains"].extend(["user_management", "subscription_billing", "tenant_isolation", "api_management"])
            domain_info["key_entities"].extend(["users", "organizations", "subscriptions", "features", "api_keys"])
            domain_info["business_model"] = "b2b"
            domain_info["target_users"].extend(["end_users", "organization_admins", "platform_admins"])
        
        # Finance domain
        elif any(word in text for word in ["finance", "banking", "payment", "transaction", "money", "account", "wallet", "financial"]):
            domain_info["primary_domain"] = "finance"
            domain_info["subdomains"].extend(["payment_processing", "account_management", "transaction_tracking", "compliance"])
            domain_info["key_entities"].extend(["accounts", "transactions", "payments", "users", "balances"])
            domain_info["target_users"].extend(["customers", "merchants", "bank_staff"])
        
        # Manufacturing domain
        elif any(word in text for word in ["manufacturing", "production", "factory", "supply", "inventory", "quality", "assembly", "warehouse"]):
            domain_info["primary_domain"] = "manufacturing"
            domain_info["subdomains"].extend(["production_planning", "quality_control", "supply_chain", "inventory_management"])
            domain_info["key_entities"].extend(["products", "materials", "production_lines", "quality_checks", "suppliers", "warehouses"])
            domain_info["target_users"].extend(["production_managers", "quality_control", "suppliers", "warehouse_staff"])
        
        # Education domain
        elif any(word in text for word in ["education", "school", "student", "teacher", "course", "learning", "academic", "university"]):
            domain_info["primary_domain"] = "education"
            domain_info["subdomains"].extend(["student_management", "course_catalog", "grade_tracking", "assignment_management"])
            domain_info["key_entities"].extend(["students", "teachers", "courses", "grades", "assignments", "departments"])
            domain_info["target_users"].extend(["students", "teachers", "administrators"])
        
        # Real Estate domain
        elif any(word in text for word in ["real estate", "property", "rental", "housing", "apartment", "lease", "landlord"]):
            domain_info["primary_domain"] = "real_estate"
            domain_info["subdomains"].extend(["property_management", "rental_tracking", "tenant_management", "maintenance"])
            domain_info["key_entities"].extend(["properties", "tenants", "leases", "payments", "maintenance_requests"])
            domain_info["target_users"].extend(["tenants", "landlords", "property_managers"])
        
        # Government domain
        elif any(word in text for word in ["government", "public", "citizen", "agency", "municipal", "federal", "state"]):
            domain_info["primary_domain"] = "government"
            domain_info["subdomains"].extend(["citizen_services", "document_management", "compliance", "public_records"])
            domain_info["key_entities"].extend(["citizens", "documents", "services", "applications", "permits"])
            domain_info["target_users"].extend(["citizens", "government_staff", "administrators"])
        
        return domain_info

    def _extract_scale_indicators(self, text: str) -> Dict[str, Any]:
        """Extract scale and performance requirements."""
        scale_info = {
            "user_count": 1000,
            "complexity_level": "moderate",
            "performance_requirements": [],
            "scaling_needs": []
        }
        
        # User count detection
        if any(word in text for word in ["million", "millions", "10m+", "enterprise", "large scale", "global", "fortune 500"]):
            scale_info["user_count"] = 1000000
            scale_info["complexity_level"] = "enterprise"
            scale_info["scaling_needs"].extend(["horizontal_scaling", "load_balancing", "distributed_architecture", "microservices"])
        elif any(word in text for word in ["thousand", "thousands", "10k+", "medium", "growing", "mid-size"]):
            scale_info["user_count"] = 10000
            scale_info["complexity_level"] = "moderate"
            scale_info["scaling_needs"].extend(["vertical_scaling", "caching", "read_replicas"])
        elif any(word in text for word in ["hundred", "100+", "small", "startup", "mvp", "local"]):
            scale_info["user_count"] = 1000
            scale_info["complexity_level"] = "simple"
        else:
            scale_info["user_count"] = 100
            scale_info["complexity_level"] = "simple"
        
        # Performance requirements
        if any(word in text for word in ["real-time", "instant", "fast", "low latency", "high performance", "responsive"]):
            scale_info["performance_requirements"].extend(["real_time_processing", "caching", "optimized_queries", "connection_pooling"])
        
        if any(word in text for word in ["high availability", "uptime", "reliability", "fault tolerance", "disaster recovery"]):
            scale_info["performance_requirements"].extend(["high_availability", "backup_strategy", "disaster_recovery", "redundancy"])
        
        if any(word in text for word in ["concurrent", "simultaneous", "multiple users", "busy"]):
            scale_info["performance_requirements"].extend(["concurrent_access", "connection_pooling", "locking_strategies"])
        
        return scale_info

    def _extract_required_features(self, text: str) -> Dict[str, Any]:
        """Extract required features and functionality."""
        features = {
            "core_features": [],
            "advanced_features": [],
            "integrations": [],
            "user_management": "basic"
        }
        
        # User management features
        if any(word in text for word in ["multi-tenant", "organization", "team", "role", "permission", "department"]):
            features["user_management"] = "advanced"
            features["core_features"].extend(["multi_tenant", "role_based_access", "organization_management", "department_hierarchy"])
        
        # Authentication features
        if any(word in text for word in ["sso", "oauth", "ldap", "active directory", "authentication", "login"]):
            features["advanced_features"].extend(["sso", "oauth", "ldap_integration", "multi_factor_auth"])
        
        # API features
        if any(word in text for word in ["api", "integration", "webhook", "rest", "graphql", "external"]):
            features["advanced_features"].extend(["api_management", "webhooks", "rate_limiting", "api_documentation"])
        
        # Analytics features
        if any(word in text for word in ["analytics", "reporting", "dashboard", "metrics", "kpi", "insights"]):
            features["advanced_features"].extend(["analytics", "reporting", "dashboard", "data_visualization"])
        
        # Search features
        if any(word in text for word in ["search", "filter", "query", "elasticsearch", "full-text"]):
            features["advanced_features"].extend(["advanced_search", "filtering", "full_text_search"])
        
        # Notification features
        if any(word in text for word in ["notification", "email", "sms", "push", "alert", "reminder"]):
            features["core_features"].extend(["notifications", "email_service", "sms_service", "push_notifications"])
        
        # Workflow features
        if any(word in text for word in ["workflow", "process", "approval", "automation", "task"]):
            features["advanced_features"].extend(["workflow_management", "approval_processes", "task_automation"])
        
        # Document management
        if any(word in text for word in ["document", "file", "upload", "storage", "attachment"]):
            features["core_features"].extend(["document_management", "file_storage", "version_control"])
        
        return features

    def _extract_compliance_requirements(self, text: str) -> Dict[str, Any]:
        """Extract compliance and security requirements."""
        compliance = {
            "standards": [],
            "security_level": "standard",
            "data_protection": [],
            "audit_requirements": False
        }
        
        # Compliance standards
        if any(word in text for word in ["hipaa", "healthcare", "medical", "patient", "phi"]):
            compliance["standards"].extend(["HIPAA"])
            compliance["security_level"] = "high"
            compliance["data_protection"].extend(["encryption", "access_control", "audit_trail", "data_minimization"])
            compliance["audit_requirements"] = True
        
        if any(word in text for word in ["gdpr", "privacy", "european", "data protection", "consent"]):
            compliance["standards"].extend(["GDPR"])
            compliance["data_protection"].extend(["data_anonymization", "right_to_erasure", "consent_management", "data_portability"])
        
        if any(word in text for word in ["sox", "sarbanes", "financial", "public company", "audit"]):
            compliance["standards"].extend(["SOX"])
            compliance["audit_requirements"] = True
        
        if any(word in text for word in ["pci", "payment", "credit card", "financial", "cardholder"]):
            compliance["standards"].extend(["PCI-DSS"])
            compliance["security_level"] = "high"
            compliance["data_protection"].extend(["encryption", "secure_transmission", "tokenization"])
        
        if any(word in text for word in ["ccpa", "california", "privacy rights"]):
            compliance["standards"].extend(["CCPA"])
            compliance["data_protection"].extend(["privacy_rights", "data_transparency"])
        
        # Security requirements
        if any(word in text for word in ["security", "secure", "encryption", "sensitive", "confidential"]):
            compliance["security_level"] = "high"
            compliance["data_protection"].extend(["encryption", "access_control", "secure_transmission"])
        
        if any(word in text for word in ["audit", "logging", "tracking", "compliance", "monitoring"]):
            compliance["audit_requirements"] = True
        
        return compliance

    def _extract_technical_requirements(self, text: str) -> Dict[str, Any]:
        """Extract technical requirements and preferences."""
        technical = {
            "database_preference": "postgresql",
            "architecture": "monolithic",
            "deployment": "cloud",
            "caching": False,
            "search": False,
            "messaging": False
        }
        
        # Database preferences
        if any(word in text for word in ["mongodb", "document", "nosql", "flexible schema"]):
            technical["database_preference"] = "mongodb"
        elif any(word in text for word in ["dynamodb", "aws", "serverless", "scalable"]):
            technical["database_preference"] = "dynamodb"
        elif any(word in text for word in ["postgresql", "postgres", "relational", "acid"]):
            technical["database_preference"] = "postgresql"
        
        # Architecture preferences
        if any(word in text for word in ["microservices", "distributed", "service-oriented", "container"]):
            technical["architecture"] = "microservices"
        
        # Infrastructure preferences
        if any(word in text for word in ["redis", "cache", "caching", "performance", "fast"]):
            technical["caching"] = True
        
        if any(word in text for word in ["elasticsearch", "search", "full-text", "indexing", "lucene"]):
            technical["search"] = True
        
        if any(word in text for word in ["kafka", "messaging", "queue", "event", "streaming", "pub-sub"]):
            technical["messaging"] = True
        
        return technical

    def generate_custom_spec_from_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a truly custom database spec based on intelligent analysis."""
        domain = analysis["domain"]
        scale = analysis["scale"]
        features = analysis["features"]
        compliance = analysis["compliance"]
        technical = analysis["technical"]
        
        # Determine database type
        db_type = technical["database_preference"]
        
        # Determine complexity level
        complexity_level = scale["complexity_level"]
        
        # Generate entities based on domain and requirements
        entities = self._generate_custom_entities(domain, features, compliance)
        
        # Generate indexes based on entities and performance requirements
        indexes = self._generate_custom_indexes(entities, scale["performance_requirements"])
        
        # Generate architecture components
        architecture = self._generate_architecture_components(technical, scale, features)
        
        # Generate security and compliance features
        security = self._generate_security_features(compliance, features)
        
        # Generate monitoring and backup strategies
        monitoring = self._generate_monitoring_strategy(scale, features)
        backup = self._generate_backup_strategy(compliance, scale)
        scaling = self._generate_scaling_strategy(scale, technical)
        
        return {
            "app_type": f"{domain['primary_domain']} application with {complexity_level} architecture and production-ready features",
            "db_type": db_type,
            "complexity_level": complexity_level,
            "entities": entities,
            "indexes": indexes,
            **architecture,
            "monitoring": monitoring,
            "backup_strategy": backup,
            "scaling_strategy": scaling,
            "security": security
        }

    def _generate_custom_entities(self, domain: Dict[str, Any], features: Dict[str, Any], compliance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate custom entities based on domain analysis."""
        entities = []
        
        # Always include users table
        users_table = {
            "name": "users",
            "fields": [
                {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                {"name": "email", "type": "string", "required": True, "unique": True},
                {"name": "password_hash", "type": "string", "required": True},
                {"name": "first_name", "type": "string", "required": True},
                {"name": "last_name", "type": "string", "required": True},
                {"name": "status", "type": "enum", "required": True, "values": ["active", "inactive", "pending"], "default": "pending"},
                {"name": "created_at", "type": "timestamp", "required": True},
                {"name": "updated_at", "type": "timestamp", "required": True}
            ]
        }
        
        # Add encryption for sensitive data
        if compliance["security_level"] == "high":
            users_table["fields"][1]["encrypted"] = True  # email
            users_table["fields"][2]["encrypted"] = True  # password_hash
        
        entities.append(users_table)
        
        # Add domain-specific entities
        for entity_name in domain["key_entities"]:
            if entity_name == "patients" and domain["primary_domain"] == "healthcare":
                entities.append(self._create_patient_entity(compliance))
            elif entity_name == "products" and domain["primary_domain"] == "ecommerce":
                entities.append(self._create_product_entity())
            elif entity_name == "organizations" and features["user_management"] == "advanced":
                entities.append(self._create_organization_entity())
            elif entity_name == "appointments" and domain["primary_domain"] == "healthcare":
                entities.append(self._create_appointment_entity())
            elif entity_name == "orders" and domain["primary_domain"] == "ecommerce":
                entities.append(self._create_order_entity())
        
        # Add audit logs if required
        if compliance["audit_requirements"]:
            entities.append(self._create_audit_log_entity())
        
        return entities

    def _create_patient_entity(self, compliance: Dict[str, Any]) -> Dict[str, Any]:
        """Create a patient entity for healthcare applications."""
        fields = [
            {"name": "id", "type": "uuid", "required": True, "primary_key": True},
            {"name": "patient_id", "type": "string", "required": True, "unique": True},
            {"name": "first_name", "type": "string", "required": True},
            {"name": "last_name", "type": "string", "required": True},
            {"name": "date_of_birth", "type": "date", "required": True},
            {"name": "phone", "type": "string", "required": False},
            {"name": "emergency_contact", "type": "jsonb", "required": False},
            {"name": "medical_history", "type": "jsonb", "required": False},
            {"name": "allergies", "type": "jsonb", "required": False},
            {"name": "status", "type": "enum", "required": True, "values": ["active", "inactive", "deceased"], "default": "active"},
            {"name": "created_at", "type": "timestamp", "required": True},
            {"name": "updated_at", "type": "timestamp", "required": True}
        ]
        
        # Add encryption for HIPAA compliance
        if "HIPAA" in compliance["standards"]:
            fields[1]["encrypted"] = True  # patient_id
            fields[2]["encrypted"] = True  # first_name
            fields[3]["encrypted"] = True  # last_name
            fields[5]["encrypted"] = True  # phone
        
        return {
            "name": "patients",
            "fields": fields
        }

    def _create_product_entity(self) -> Dict[str, Any]:
        """Create a product entity for e-commerce applications."""
        return {
            "name": "products",
            "fields": [
                {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                {"name": "sku", "type": "string", "required": True, "unique": True},
                {"name": "name", "type": "string", "required": True},
                {"name": "description", "type": "text", "required": False},
                {"name": "price", "type": "decimal", "required": True, "precision": 10, "scale": 2},
                {"name": "inventory_count", "type": "integer", "required": True, "default": 0},
                {"name": "category", "type": "string", "required": False},
                {"name": "status", "type": "enum", "required": True, "values": ["active", "inactive", "discontinued"], "default": "active"},
                {"name": "created_at", "type": "timestamp", "required": True},
                {"name": "updated_at", "type": "timestamp", "required": True}
            ]
        }

    def _create_organization_entity(self) -> Dict[str, Any]:
        """Create an organization entity for multi-tenant applications."""
        return {
            "name": "organizations",
            "fields": [
                {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                {"name": "name", "type": "string", "required": True},
                {"name": "slug", "type": "string", "required": True, "unique": True},
                {"name": "description", "type": "text", "required": False},
                {"name": "settings", "type": "jsonb", "required": False},
                {"name": "status", "type": "enum", "required": True, "values": ["active", "inactive", "suspended"], "default": "active"},
                {"name": "created_at", "type": "timestamp", "required": True},
                {"name": "updated_at", "type": "timestamp", "required": True}
            ]
        }

    def _create_appointment_entity(self) -> Dict[str, Any]:
        """Create an appointment entity for healthcare applications."""
        return {
            "name": "appointments",
            "fields": [
                {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                {"name": "patient_id", "type": "uuid", "required": True, "foreign_key": {"table": "patients", "field": "id"}},
                {"name": "doctor_id", "type": "uuid", "required": True, "foreign_key": {"table": "users", "field": "id"}},
                {"name": "appointment_date", "type": "timestamp", "required": True},
                {"name": "duration_minutes", "type": "integer", "required": True, "default": 30},
                {"name": "status", "type": "enum", "required": True, "values": ["scheduled", "confirmed", "completed", "cancelled"], "default": "scheduled"},
                {"name": "notes", "type": "text", "required": False},
                {"name": "created_at", "type": "timestamp", "required": True},
                {"name": "updated_at", "type": "timestamp", "required": True}
            ]
        }

    def _create_order_entity(self) -> Dict[str, Any]:
        """Create an order entity for e-commerce applications."""
        return {
            "name": "orders",
            "fields": [
                {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                {"name": "customer_id", "type": "uuid", "required": True, "foreign_key": {"table": "users", "field": "id"}},
                {"name": "order_number", "type": "string", "required": True, "unique": True},
                {"name": "total_amount", "type": "decimal", "required": True, "precision": 10, "scale": 2},
                {"name": "status", "type": "enum", "required": True, "values": ["pending", "processing", "shipped", "delivered", "cancelled"], "default": "pending"},
                {"name": "shipping_address", "type": "jsonb", "required": True},
                {"name": "created_at", "type": "timestamp", "required": True},
                {"name": "updated_at", "type": "timestamp", "required": True}
            ]
        }

    def _create_audit_log_entity(self) -> Dict[str, Any]:
        """Create an audit log entity for compliance requirements."""
        return {
            "name": "audit_logs",
            "fields": [
                {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                {"name": "table_name", "type": "string", "required": True},
                {"name": "record_id", "type": "uuid", "required": True},
                {"name": "action", "type": "enum", "required": True, "values": ["insert", "update", "delete", "view"]},
                {"name": "old_values", "type": "jsonb", "required": False},
                {"name": "new_values", "type": "jsonb", "required": False},
                {"name": "user_id", "type": "uuid", "required": False},
                {"name": "ip_address", "type": "inet", "required": False},
                {"name": "created_at", "type": "timestamp", "required": True}
            ]
        }

    def _generate_custom_indexes(self, entities: List[Dict[str, Any]], performance_requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate custom indexes based on entities and performance requirements."""
        indexes = []
        
        for entity in entities:
            entity_name = entity["name"]
            fields = entity["fields"]
            
            # Create indexes for unique fields
            for field in fields:
                if field.get("unique"):
                    indexes.append({
                        "name": f"idx_{entity_name}_{field['name']}",
                        "table": entity_name,
                        "fields": [{"field": field["name"], "type": "btree"}],
                        "unique": True
                    })
            
            # Create indexes for foreign keys
            for field in fields:
                if field.get("foreign_key"):
                    indexes.append({
                        "name": f"idx_{entity_name}_{field['name']}",
                        "table": entity_name,
                        "fields": [{"field": field["name"], "type": "btree"}],
                        "unique": False
                    })
            
            # Create indexes for commonly queried fields
            if entity_name == "users":
                indexes.append({
                    "name": f"idx_{entity_name}_status",
                    "table": entity_name,
                    "fields": [{"field": "status", "type": "btree"}],
                    "unique": False
                })
            elif entity_name == "appointments":
                indexes.append({
                    "name": f"idx_{entity_name}_date",
                    "table": entity_name,
                    "fields": [{"field": "appointment_date", "type": "btree"}],
                    "unique": False
                })
            elif entity_name == "orders":
                indexes.append({
                    "name": f"idx_{entity_name}_status",
                    "table": entity_name,
                    "fields": [{"field": "status", "type": "btree"}],
                    "unique": False
                })
        
        return indexes

    def _generate_architecture_components(self, technical: Dict[str, Any], scale: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate architecture components based on requirements."""
        components = {}
        
        # Add caching if required
        if technical["caching"] or scale["complexity_level"] == "enterprise":
            components["caching_strategy"] = {
                "redis": {
                    "user_sessions": {"ttl": 3600, "pattern": "session:{session_id}"},
                    "user_cache": {"ttl": 1800, "pattern": "user:{user_id}"}
                }
            }
        
        # Add search if required
        if technical["search"] or "advanced_search" in features["advanced_features"]:
            components["search_strategy"] = {
                "elasticsearch": {
                    "users_index": {
                        "mappings": {
                            "properties": {
                                "email": {"type": "keyword"},
                                "first_name": {"type": "text", "analyzer": "standard"},
                                "last_name": {"type": "text", "analyzer": "standard"}
                            }
                        }
                    }
                }
            }
        
        # Add hybrid architecture for enterprise
        if scale["complexity_level"] == "enterprise":
            components["hybrid_architecture"] = ["redis", "elasticsearch", "s3"]
            if technical["messaging"]:
                components["hybrid_architecture"].append("kafka")
        
        return components

    def _generate_security_features(self, compliance: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security features based on compliance requirements."""
        security = {
            "encryption": {"at_rest": True, "in_transit": True},
            "access_control": {"rbac": True},
            "compliance": compliance["standards"]
        }
        
        # Add field-level encryption for high security
        if compliance["security_level"] == "high":
            security["encryption"]["field_level"] = ["email", "password_hash", "phone"]
        
        # Add advanced access control for multi-tenant
        if features["user_management"] == "advanced":
            security["access_control"]["multi_tenant"] = True
            security["access_control"]["api_keys"] = True
        
        return security

    def _generate_monitoring_strategy(self, scale: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate monitoring strategy based on scale and features."""
        monitoring = {
            "performance_metrics": ["query_response_time", "active_sessions"],
            "business_metrics": ["user_registrations", "user_logins"],
            "alerts": ["high_latency", "failed_logins"]
        }
        
        # Add more metrics for enterprise
        if scale["complexity_level"] == "enterprise":
            monitoring["performance_metrics"].extend(["connection_pool_usage", "cache_hit_ratio", "error_rate"])
            monitoring["business_metrics"].extend(["api_usage", "feature_usage", "user_retention"])
            monitoring["alerts"].extend(["low_cache_hit_ratio", "high_error_rate", "unusual_traffic_patterns"])
        
        return monitoring

    def _generate_backup_strategy(self, compliance: Dict[str, Any], scale: Dict[str, Any]) -> Dict[str, Any]:
        """Generate backup strategy based on compliance and scale."""
        backup = {
            "postgresql": {"frequency": "daily", "retention": "7_days", "encryption": True}
        }
        
        # Enhanced backup for enterprise
        if scale["complexity_level"] == "enterprise":
            backup["postgresql"]["frequency"] = "hourly"
            backup["postgresql"]["retention"] = "30_days"
        
        # Add Redis backup if caching is used
        if "redis" in str(compliance):
            backup["redis"] = {"frequency": "hourly", "retention": "3_days"}
        
        return backup

    def _generate_scaling_strategy(self, scale: Dict[str, Any], technical: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scaling strategy based on scale and technical requirements."""
        scaling = {
            "vertical_scaling": {"initial_cpu": "2_cores", "initial_memory": "8GB", "max_cpu": "8_cores", "max_memory": "32GB"}
        }
        
        # Enhanced scaling for enterprise
        if scale["complexity_level"] == "enterprise":
            scaling["vertical_scaling"] = {"initial_cpu": "8_cores", "initial_memory": "32GB", "max_cpu": "32_cores", "max_memory": "128GB"}
            scaling["horizontal_scaling"] = {
                "postgresql": {"read_replicas": 5, "sharding": "by_organization_id"},
                "redis": {"cluster_mode": True, "nodes": 12}
            }
        
        return scaling

# Test the intelligent agent
if __name__ == "__main__":
    agent = IntelligentAIAgent()
    
    # Test with healthcare description
    healthcare_text = "Healthcare management system for a large hospital with 50,000+ patients, HIPAA compliance, medical records, appointments, and audit trails"
    
    analysis = agent.analyze_business_requirements(healthcare_text)
    spec = agent.generate_custom_spec_from_analysis(analysis)
    
    print("Healthcare Analysis:")
    print(f"Domain: {analysis['domain']['primary_domain']}")
    print(f"Scale: {analysis['scale']['complexity_level']}")
    print(f"Compliance: {analysis['compliance']['standards']}")
    print(f"Entities: {len(spec['entities'])}")
    print(f"Database: {spec['db_type']}")
    
    # Test with e-commerce description
    ecommerce_text = "E-commerce platform for selling products online, inventory management, order processing, payment handling, and customer management"
    
    analysis2 = agent.analyze_business_requirements(ecommerce_text)
    spec2 = agent.generate_custom_spec_from_analysis(analysis2)
    
    print("\nE-commerce Analysis:")
    print(f"Domain: {analysis2['domain']['primary_domain']}")
    print(f"Scale: {analysis2['scale']['complexity_level']}")
    print(f"Entities: {len(spec2['entities'])}")
    print(f"Database: {spec2['db_type']}")
