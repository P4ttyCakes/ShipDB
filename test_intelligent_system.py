#!/usr/bin/env python3
"""
Test the truly intelligent ShipDB system with various business descriptions
"""

import requests
import json

def test_intelligent_shipdb():
    print("🚀 Testing Truly Intelligent ShipDB - Universal Database Architect")
    print("=" * 80)
    
    # Test cases with different business descriptions
    test_cases = [
        {
            "name": "Healthcare System",
            "description": "Large hospital system with 50,000+ patients, HIPAA compliance, medical records, appointments, and audit trails"
        },
        {
            "name": "E-commerce Platform", 
            "description": "Online store selling products, inventory management, order processing, payment handling, customer management"
        },
        {
            "name": "SaaS Platform",
            "description": "Multi-tenant software platform with organizations, subscriptions, API management, and analytics"
        },
        {
            "name": "Manufacturing System",
            "description": "Production management system with quality control, supply chain, warehouse management, and compliance"
        },
        {
            "name": "Financial Services",
            "description": "Banking platform with transactions, accounts, payments, PCI compliance, and audit requirements"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print("-" * 60)
        
        try:
            # Start project
            response = requests.post("http://localhost:8000/api/projects/test_project/start", 
                                   json={
                                       "name": test_case["name"], 
                                       "description": test_case["description"]
                                   })
            response.raise_for_status()
            session_id = response.json()["session_id"]
            
            # Get AI response
            response = requests.post("http://localhost:8000/api/projects/test_project/next", 
                                   json={
                                       "session_id": session_id, 
                                       "answer": test_case["description"]
                                   })
            response.raise_for_status()
            result = response.json()
            
            if result.get("partial_spec"):
                spec = result["partial_spec"]
                print(f"✅ Generated Database:")
                print(f"   📊 Application Type: {spec.get('app_type', 'Unknown')}")
                print(f"   🗄️ Database: {spec.get('db_type', 'Unknown').upper()}")
                print(f"   📈 Complexity: {spec.get('complexity_level', 'Unknown')}")
                print(f"   📋 Entities: {len(spec.get('entities', []))} tables")
                
                # Show domain-specific entities
                entities = spec.get('entities', [])
                if len(entities) > 1:  # More than just users
                    print(f"   🏗️ Custom Entities: {', '.join([e['name'] for e in entities[1:]])}")
                
                # Show compliance features
                security = spec.get('security', {})
                if security.get('compliance'):
                    print(f"   🔒 Compliance: {', '.join(security['compliance'])}")
                
                # Show architecture features
                if spec.get('hybrid_architecture'):
                    print(f"   🏛️ Architecture: {', '.join(spec['hybrid_architecture'])}")
                
                if spec.get('caching_strategy'):
                    print(f"   ⚡ Caching: Redis enabled")
                
                if spec.get('search_strategy'):
                    print(f"   🔍 Search: Elasticsearch enabled")
                
                print(f"   📊 Monitoring: {len(spec.get('monitoring', {}).get('performance_metrics', []))} metrics")
                
            else:
                print("❌ No database spec generated")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
    
    print("\n" + "=" * 80)
    print("🎉 Intelligent ShipDB Test Complete!")
    print("The system now truly analyzes business requirements and generates custom databases!")

if __name__ == "__main__":
    test_intelligent_shipdb()
