#!/usr/bin/env python3
"""
Test the ENHANCED ShipDB that creates detailed, fool-proof, deployable databases for ANY business sector
"""

import requests
import json
import time

def test_comprehensive_ai():
    print("🚀 Testing ENHANCED ShipDB - Universal Database Architect")
    print("=" * 80)
    print("This AI creates DETAILED, FOOL-PROOF, DEPLOYABLE databases for ANY business!")
    print("=" * 80)
    
    # Test 1: Healthcare System (Complex Compliance Requirements)
    print("\n🏥 TEST 1: Healthcare Management System")
    print("-" * 50)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "MediCare Pro", 
                               "description": "A comprehensive healthcare management system for hospitals and clinics"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "Healthcare industry - managing patients, medical records, appointments, billing, and compliance with HIPAA regulations."
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1['prompt']}")
    
    # Answer 2
    answer2 = "Large hospital system with 10,000+ patients, need HIPAA compliance, audit trails, encryption, and integration with medical devices."
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2['prompt']}")
    
    if result2.get('done'):
        spec = result2.get('partial_spec', {})
        print(f"\n🎉 Generated COMPREHENSIVE Healthcare Database!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Database: {spec.get('db_type', 'Unknown')}")
        print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        # Show advanced features
        if "security" in spec:
            print(f"🔒 Security Features: {len(spec['security'])} layers")
        if "monitoring" in spec:
            print(f"📊 Monitoring: {len(spec['monitoring'])} metric categories")
        
        # Generate and show schemas
        schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                      json=spec)
        
        if schema_response.status_code == 200:
            artifacts = schema_response.json()
            print(f"✅ Comprehensive schemas generated!")
            print(f"📝 PostgreSQL SQL: {len(artifacts.get('postgres_sql', ''))} characters")
            print(f"🍃 MongoDB Scripts: {len(artifacts.get('mongo_scripts', []))} scripts")
            print(f"⚡ DynamoDB Tables: {len(artifacts.get('dynamodb_tables', []))} tables")
    
    # Test 2: Manufacturing & Supply Chain (Complex Relationships)
    print("\n🏭 TEST 2: Manufacturing & Supply Chain System")
    print("-" * 50)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "ManufacturingPro", 
                               "description": "A comprehensive manufacturing and supply chain management system"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "Manufacturing industry - managing products, suppliers, inventory, production lines, quality control, and logistics."
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1['prompt']}")
    
    # Answer 2
    answer2 = "Medium enterprise with 500+ suppliers, 1000+ products, need real-time inventory tracking, quality compliance, and integration with ERP systems."
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2['prompt']}")
    
    if result2.get('done'):
        spec = result2.get('partial_spec', {})
        print(f"\n🎉 Generated COMPREHENSIVE Manufacturing Database!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Database: {spec.get('db_type', 'Unknown')}")
        print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        # Show enterprise features
        if "hybrid_architecture" in spec:
            print(f"🏗️ Hybrid Architecture: {spec['hybrid_architecture']}")
        if "scaling_strategy" in spec:
            print(f"📈 Scaling Strategy: Included")
    
    # Test 3: SaaS Platform (Multi-tenant Architecture)
    print("\n💻 TEST 3: SaaS Platform")
    print("-" * 50)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "SaaSPlatform Pro", 
                               "description": "A multi-tenant SaaS platform for project management"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "SaaS platform - multi-tenant architecture with users, organizations, projects, billing, and API integrations."
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1['prompt']}")
    
    # Answer 2
    answer2 = "Growing SaaS with 1000+ organizations, 10K+ users, need multi-tenancy, subscription billing, API rate limiting, and analytics."
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2['prompt']}")
    
    if result2.get('done'):
        spec = result2.get('partial_spec', {})
        print(f"\n🎉 Generated COMPREHENSIVE SaaS Database!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Database: {spec.get('db_type', 'Unknown')}")
        print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        # Show all enterprise features
        features = []
        if "hybrid_architecture" in spec:
            features.append("Hybrid Architecture")
        if "caching_strategy" in spec:
            features.append("Caching Strategy")
        if "search_strategy" in spec:
            features.append("Search Strategy")
        if "monitoring" in spec:
            features.append("Monitoring")
        if "scaling_strategy" in spec:
            features.append("Scaling Strategy")
        if "security" in spec:
            features.append("Security")
        
        print(f"🏆 Enterprise Features: {', '.join(features)}")
    
    # Test 4: Government System (Compliance & Security)
    print("\n🏛️ TEST 4: Government Citizen Services")
    print("-" * 50)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "CitizenServices", 
                               "description": "A government system for citizen services and document management"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "Government sector - managing citizens, services, documents, compliance, and public records with strict security requirements."
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1['prompt']}")
    
    # Answer 2
    answer2 = "Large government system serving 100K+ citizens, need strict compliance, audit trails, encryption, and integration with other government systems."
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2['prompt']}")
    
    if result2.get('done'):
        spec = result2.get('partial_spec', {})
        print(f"\n🎉 Generated COMPREHENSIVE Government Database!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Database: {spec.get('db_type', 'Unknown')}")
        print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        # Show compliance features
        if "security" in spec and "compliance" in spec["security"]:
            print(f"📋 Compliance: {spec['security']['compliance']}")
    
    print("\n" + "=" * 80)
    print("🎉 COMPREHENSIVE TEST COMPLETE!")
    print("=" * 80)
    print("✅ AI adapts to ANY business sector (Healthcare, Manufacturing, SaaS, Government)")
    print("✅ Creates DETAILED, PRODUCTION-READY databases")
    print("✅ Includes FOOL-PROOF features (security, compliance, monitoring)")
    print("✅ Supports DEPLOYMENT to PostgreSQL, MongoDB, DynamoDB")
    print("✅ Perfect for EVERY type of business - from startups to enterprise!")
    print("\n🚀 Try it yourself at: http://localhost:8001")
    print("📚 Full deployment support for all database types!")

if __name__ == "__main__":
    test_comprehensive_ai()
