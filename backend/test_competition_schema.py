#!/usr/bin/env python3
"""
Test Competition Schema Deployment to Supabase
Simulates Claude processing the SQL schema and generates execution instructions
"""

import os
from dotenv import load_dotenv
from claude_supabase_driver import call_supabase_function

load_dotenv()

def main():
    print("=" * 70)
    print("Competition Schema Deployment Test")
    print("=" * 70)
    
    # The schema the user provided
    schema = """
CREATE TABLE IF NOT EXISTS "competitions" (
  "id" UUID NOT NULL,
  "name" TEXT NOT NULL,
  "description" TEXT,
  "start_date" DATE NOT NULL,
  "end_date" DATE NOT NULL,
  "location" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS "participants" (
  "id" UUID NOT NULL,
  "competition_id" UUID NOT NULL,
  "name" TEXT NOT NULL,
  "email" TEXT NOT NULL,
  "phone" TEXT,
  "created_at" TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS "results" (
  "id" UUID NOT NULL,
  "competition_id" UUID NOT NULL,
  "participant_id" UUID NOT NULL,
  "rank" INTEGER NOT NULL,
  "score" DOUBLE PRECISION NOT NULL,
  "created_at" TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS "leaderboard" (
  "id" UUID NOT NULL,
  "competition_id" UUID NOT NULL,
  "participant_id" UUID NOT NULL,
  "total_score" DOUBLE PRECISION NOT NULL,
  "rank" INTEGER NOT NULL,
  "updated_at" TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS "media" (
  "id" UUID NOT NULL,
  "competition_id" UUID NOT NULL,
  "participant_id" UUID NOT NULL,
  "type" TEXT NOT NULL,
  "url" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL
);
"""
    
    print("\n📋 Schema to Deploy:")
    print("=" * 70)
    print(schema)
    
    # Test calling the create_table function
    print("\n🔧 Calling Claude Supabase Driver...")
    result = call_supabase_function("create_table", table_schema=schema)
    
    print("\n📤 Result:")
    print("=" * 70)
    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    
    if result.get('schema'):
        print("\n📋 Copy this SQL and run it in Supabase Dashboard:")
        print("=" * 70)
        print(result['schema'])
    
    if result.get('instructions'):
        print(f"\n💡 {result['instructions']}")
    
    if result.get('note'):
        print(f"\n⚠️  Note: {result['note']}")
    
    print("\n" + "=" * 70)
    print("✅ Schema prepared successfully!")
    print("=" * 70)
    print("\n📝 Next Steps:")
    print("1. Go to your Supabase Dashboard: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to SQL Editor")
    print("4. Paste the SQL above")
    print("5. Click 'Run' to execute")
    print("6. Tables will be created in your database")
    print("=" * 70)

if __name__ == "__main__":
    main()

