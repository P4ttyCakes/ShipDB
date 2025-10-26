#!/usr/bin/env python3
"""
Test deploying competition database schema to Supabase
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv('./backend/.env')

sys.path.insert(0, 'backend')
from claude_supabase_driver import call_supabase_function

# Competition database schema
competition_schema = '''
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
'''

print("=" * 70)
print("Testing Competition Database Deployment to Supabase")
print("=" * 70)

# Deploy
print("\n📋 Deploying competition database schema...")
result = call_supabase_function('create_table', table_schema=competition_schema)

print(f"\n✅ Deployment Result:")
print(f"   Success: {result.get('success')}")
print(f"   Method: {result.get('method')}")
print(f"   Tables Created: {result.get('tables_created', [])}")
print(f"   RLS Enabled: {result.get('rls_enabled', False)}")

# Verify tables exist
from supabase import create_client
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("\n🔍 Verifying tables exist...")
expected_tables = ['competitions', 'participants', 'results', 'leaderboard', 'media']
for table in expected_tables:
    try:
        rows = supabase.table(table).select("*").limit(1).execute()
        print(f"   ✅ {table} exists (rows: {len(rows.data)})")
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg:
            print(f"   ❌ {table} not found")
        else:
            print(f"   ⚠️  {table} - {error_msg[:80]}")

print("\n" + "=" * 70)
print("✅ Competition database deployment test complete!")
print("=" * 70)

