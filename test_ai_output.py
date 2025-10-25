#!/usr/bin/env python3
"""
Test what the AI actually generates
"""

import requests
import json

def test_ai_output():
    base_url = "http://localhost:8000"
    
    # Start session
    response = requests.post(f"{base_url}/api/projects/new_project/start", 
                           json={"name": "Test", "description": "Test"})
    session_id = response.json()["session_id"]
    
    # Answer with detailed field types
    answer = """A blog application with:
    - Users table: id (integer), name (text), email (text)
    - Posts table: id (integer), title (text), content (text), author_id (integer)  
    - Comments table: id (integer), content (text), post_id (integer), author_id (integer)
    Use PostgreSQL database with primary keys and foreign key relationships."""
    
    response = requests.post(f"{base_url}/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer})
    result = response.json()
    
    print("AI Generated Spec:")
    print(json.dumps(result['partial_spec'], indent=2))
    
    # Finalize
    response = requests.post(f"{base_url}/api/projects/new_project/finish", 
                           json={"session_id": session_id})
    final_result = response.json()
    
    print("\nFinal Spec:")
    print(json.dumps(final_result['spec'], indent=2))

if __name__ == "__main__":
    test_ai_output()
