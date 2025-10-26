#!/usr/bin/env python3
"""
Test Automatic Schema Deployment to Supabase
Demonstrates fully automated table creation without manual copy-paste
"""

import os
import requests
from dotenv import load_dotenv
from claude_supabase_driver import call_supabase_function

load_dotenv()

def execute_sql_via_rest_api(sql_query: str):
    """Execute SQL directly via Supabase REST API"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            return {"success": False, "error": "Missing Supabase credentials"}
        
        # Try to execute SQL via REST API
        rest_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'query': sql_query
        }
        
        response = requests.post(rest_url, headers=headers, json=data)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "SQL executed via REST API",
                "response": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"REST API error: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    print("=" * 70)
    print("Automatic Schema Deployment Test")
    print("=" * 70)
    
    # Check if DB URL is configured
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        print("\n❌ SUPABASE_DB_URL not configured!")
        print("\nTo enable automatic deployment, add to your .env file:")
        print("SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres")
        print("\nYou can find your database password in Supabase Dashboard > Settings > Database")
        return
    
    print(f"\n✅ Database connection configured")
    
    # Competition schema
    schema = """
CREATE TABLE IF NOT EXISTS "competitions" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "name" TEXT NOT NULL,
  "description" TEXT,
  "start_date" DATE NOT NULL,
  "end_date" DATE NOT NULL,
  "location" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "participants" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "competition_id" UUID NOT NULL,
  "name" TEXT NOT NULL,
  "email" TEXT NOT NULL,
  "phone" TEXT,
  "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY ("competition_id") REFERENCES "competitions"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "results" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "competition_id" UUID NOT NULL,
  "participant_id" UUID NOT NULL,
  "rank" INTEGER NOT NULL,
  "score" DOUBLE PRECISION NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY ("competition_id") REFERENCES "competitions"("id") ON DELETE CASCADE,
  FOREIGN KEY ("participant_id") REFERENCES "participants"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "leaderboard" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "competition_id" UUID NOT NULL,
  "participant_id" UUID NOT NULL,
  "total_score" DOUBLE PRECISION NOT NULL,
  "rank" INTEGER NOT NULL,
  "updated_at" TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY ("competition_id") REFERENCES "competitions"("id") ON DELETE CASCADE,
  FOREIGN KEY ("participant_id") REFERENCES "participants"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "media" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "competition_id" UUID NOT NULL,
  "participant_id" UUID NOT NULL,
  "type" TEXT NOT NULL,
  "url" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY ("competition_id") REFERENCES "competitions"("id") ON DELETE CASCADE,
  FOREIGN KEY ("participant_id") REFERENCES "participants"("id") ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_participants_competition_id ON "participants"("competition_id");
CREATE INDEX IF NOT EXISTS idx_results_competition_id ON "results"("competition_id");
CREATE INDEX IF NOT EXISTS idx_results_participant_id ON "results"("participant_id");
CREATE INDEX IF NOT EXISTS idx_leaderboard_competition_id ON "leaderboard"("competition_id");
CREATE INDEX IF NOT EXISTS idx_leaderboard_participant_id ON "leaderboard"("participant_id");
CREATE INDEX IF NOT EXISTS idx_media_competition_id ON "media"("competition_id");
CREATE INDEX IF NOT EXISTS idx_media_participant_id ON "media"("participant_id");
"""
    
    print("\n📋 Deploying Competition Schema...")
    print("=" * 70)
    
    # Try direct REST API execution first
    print("\n🔧 Trying direct REST API execution...")
    result = execute_sql_via_rest_api(schema)
    
    if result.get('success'):
        print("✅ Schema deployed successfully via REST API!")
        print(f"Response: {result.get('response')}")
    else:
        print(f"❌ REST API failed: {result.get('error')}")
        
        # Fallback to driver method
        print("\n🔧 Trying driver method...")
        result = call_supabase_function("create_table", table_schema=schema)
        
        print("\n📤 Deployment Result:")
        print("=" * 70)
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        
        if result.get('tables_created'):
            print(f"Tables Created: {', '.join(result['tables_created'])}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        if result.get('instructions'):
            print(f"\n💡 {result['instructions']}")
    
    print("\n" + "=" * 70)
    if result.get('success'):
        print("✅ Schema deployed successfully!")
        print("Check your Supabase dashboard to verify tables were created.")
    else:
        print("❌ Deployment failed")
    print("=" * 70)

if __name__ == "__main__":
    main()
