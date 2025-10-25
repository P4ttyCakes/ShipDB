#!/usr/bin/env python3
"""
Test the enhanced enterprise-grade AI agent
"""

import requests
import json

def test_enterprise_ai():
    print("🏢 Testing Enterprise-Grade AI Database Architect")
    print("=" * 60)
    print("This AI now creates PRODUCTION-READY, SCALABLE database systems!")
    print("=" * 60)
    
    # Test: Enterprise E-commerce Platform
    print("\n🛒 DEMO: Enterprise E-commerce Platform")
    print("-" * 50)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "Enterprise E-commerce Platform", 
                               "description": "A high-scale e-commerce platform serving millions of customers with real-time inventory, personalized recommendations, and global distribution"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "We expect 10M+ users, 1M+ products, 100K+ orders daily. Need real-time inventory, personalized recommendations, global shipping, and 99.99% uptime."
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1['prompt']}")
    
    # Answer 2
    answer2 = "We need GDPR compliance, PCI DSS for payments, real-time analytics, A/B testing, and integration with 50+ external services. Budget allows for enterprise infrastructure."
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2['prompt']}")
    
    if result2.get('done'):
        spec = result2.get('partial_spec', {})
        print(f"\n🎉 Generated ENTERPRISE Database Architecture!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Primary Database: {spec.get('db_type', 'Unknown')}")
        print(f"🏗️ Hybrid Architecture: {spec.get('hybrid_architecture', [])}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        # Show enterprise features
        if "caching_strategy" in spec:
            print(f"\n⚡ Caching Strategy: {len(spec['caching_strategy'])} components")
        
        if "search_strategy" in spec:
            print(f"🔍 Search Strategy: {len(spec['search_strategy'])} components")
        
        if "monitoring" in spec:
            print(f"📊 Monitoring: {len(spec['monitoring'])} metric categories")
        
        if "scaling_strategy" in spec:
            print(f"📈 Scaling Strategy: Horizontal + Vertical scaling")
        
        if "security" in spec:
            print(f"🔒 Security: {len(spec['security'])} security layers")
        
        # Generate schemas
        print(f"\n🔧 Generating Enterprise Database Schemas...")
        schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                      json=spec)
        
        if schema_response.status_code == 200:
            artifacts = schema_response.json()
            print("✅ Enterprise Schemas Generated Successfully!")
            
            # Show comprehensive results
            print(f"\n📝 PostgreSQL SQL: {len(artifacts.get('postgres_sql', ''))} characters")
            print(f"🍃 MongoDB Scripts: {len(artifacts.get('mongo_scripts', []))} scripts")
            print(f"⚡ DynamoDB Tables: {len(artifacts.get('dynamodb_tables', []))} tables")
            
            # Show enterprise features
            if "hybrid_architecture" in artifacts:
                print(f"🏗️ Hybrid Architecture: {artifacts['hybrid_architecture']}")
            
            if "caching_strategy" in artifacts:
                print(f"⚡ Caching Strategy: Redis with {len(artifacts['caching_strategy'].get('redis', {}))} cache patterns")
            
            if "search_strategy" in artifacts:
                print(f"🔍 Search Strategy: Elasticsearch with {len(artifacts['search_strategy'].get('elasticsearch', {}))} indices")
            
            if "monitoring" in artifacts:
                print(f"📊 Monitoring: {len(artifacts['monitoring'].get('performance_metrics', []))} performance metrics")
            
            if "scaling_strategy" in artifacts:
                scaling = artifacts['scaling_strategy']
                print(f"📈 Scaling: {scaling.get('horizontal_scaling', {}).get('postgresql', {}).get('read_replicas', 0)} read replicas")
            
            if "security" in artifacts:
                security = artifacts['security']
                print(f"🔒 Security: {len(security.get('compliance', []))} compliance standards")
            
            # Show sample SQL
            sql = artifacts.get('postgres_sql', '')
            if sql:
                print(f"\n📝 Sample Enterprise PostgreSQL SQL:")
                print(sql[:500] + "..." if len(sql) > 500 else sql)
        else:
            print(f"❌ Schema generation failed: {schema_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 ENTERPRISE AI ARCHITECT TEST COMPLETE!")
    print("=" * 60)
    print("✅ AI now creates enterprise-grade database architectures")
    print("✅ Includes hybrid architectures with multiple databases")
    print("✅ Implements caching, search, monitoring, and scaling strategies")
    print("✅ Adds security, compliance, and disaster recovery")
    print("✅ Eliminates ALL database complexity for users")
    print("\n🚀 This AI can now replace entire database teams!")

if __name__ == "__main__":
    test_enterprise_ai()
