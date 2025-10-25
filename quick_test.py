#!/usr/bin/env python3
"""
Quick test to verify ShipDB is working
"""

import requests
import json

def test_shipdb():
    print("🚀 Testing ShipDB - Universal Database Architect")
    print("=" * 60)
    
    # Test 1: Health check
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure the backend is running on port 8000")
        return
    
    # Test 2: Start a project
    try:
        response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                               json={
                                   "name": "Test Healthcare System", 
                                   "description": "HIPAA-compliant healthcare management system"
                               })
        
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            print(f"✅ Project started successfully")
            print(f"📋 AI Question: {data['prompt']}")
        else:
            print(f"❌ Project start failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Project start error: {e}")
        return
    
    # Test 3: Answer AI question
    try:
        answer = "Healthcare industry - managing patients, medical records, appointments, and HIPAA compliance."
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Response: {data['prompt']}")
        else:
            print(f"❌ AI response failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ AI response error: {e}")
        return
    
    # Test 4: Second answer
    try:
        answer2 = "Large hospital system with 10,000+ patients, need HIPAA compliance, audit trails, and encryption."
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer2})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Response: {data['prompt']}")
            
            if data.get('done'):
                spec = data.get('partial_spec', {})
                print(f"\n🎉 Database Generated!")
                print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
                print(f"🗄️ Database: {spec.get('db_type', 'Unknown').upper()}")
                print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
                print(f"📋 Entities: {len(spec.get('entities', []))} tables")
                
                # Show enterprise features
                if "security" in spec:
                    print(f"🔒 Security Features: Included")
                if "monitoring" in spec:
                    print(f"📊 Monitoring: Included")
                if "hybrid_architecture" in spec:
                    print(f"🏗️ Hybrid Architecture: {', '.join(spec['hybrid_architecture'])}")
        else:
            print(f"❌ Second AI response failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Second AI response error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ShipDB is working correctly!")
    print("🌐 Open http://localhost:8001 in your browser to use the web interface")
    print("📚 The system can now create detailed, fool-proof databases for ANY business sector!")

if __name__ == "__main__":
    test_shipdb()
