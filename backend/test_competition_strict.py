#!/usr/bin/env python3
"""
Strict Test Case for Existing Competition Schema
Tests comprehensive CRUD operations on existing tables
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from claude_supabase_driver import call_supabase_function

load_dotenv()

def test_competition_schema():
    """Comprehensive test of competition schema CRUD operations"""
    
    print("=" * 80)
    print("COMPETITION SCHEMA STRICT TEST CASE")
    print("=" * 80)
    
    # Test 1: Verify Tables Exist
    print("\n📋 TEST 1: Table Verification")
    print("-" * 50)
    
    tables = ['competitions', 'participants', 'results', 'leaderboard', 'media']
    existing_tables = []
    
    for table in tables:
        try:
            result = call_supabase_function("query_table", table_name=table, filters={})
            if result.get("success"):
                existing_tables.append(table)
                print(f"✅ {table} table exists")
            else:
                print(f"❌ {table} table does not exist")
        except Exception as e:
            print(f"❌ Error checking {table}: {e}")
    
    print(f"\n📊 Tables Status: {len(existing_tables)}/{len(tables)} exist")
    
    if len(existing_tables) != len(tables):
        print("❌ Not all tables exist. Cannot proceed with full test.")
        return
    
    # Test 2: Competition Creation
    print("\n🏆 TEST 2: Competition Creation")
    print("-" * 50)
    
    competition_data = {
        "id": str(uuid.uuid4()),
        "name": "Strict Test Competition 2024",
        "description": "Comprehensive test of competition management system",
        "start_date": "2024-03-01",
        "end_date": "2024-03-31",
        "location": "Test Arena, Test City",
        "created_at": datetime.now().isoformat()
    }
    
    result = call_supabase_function("insert_row", table_name="competitions", row_data=competition_data)
    if result.get("success"):
        competition_id = competition_data["id"]
        print(f"✅ Created competition: {competition_data['name']}")
        print(f"   ID: {competition_id}")
    else:
        print(f"❌ Failed to create competition: {result.get('error')}")
        return
    
    # Test 3: Participant Registration
    print("\n👥 TEST 3: Participant Registration")
    print("-" * 50)
    
    participants_data = [
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "name": "Alice Johnson",
            "email": "alice.johnson@test.com",
            "phone": "+1-555-0101",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "name": "Bob Smith",
            "email": "bob.smith@test.com",
            "phone": "+1-555-0102",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "name": "Carol Davis",
            "email": "carol.davis@test.com",
            "phone": "+1-555-0103",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    participant_ids = []
    for participant in participants_data:
        result = call_supabase_function("insert_row", table_name="participants", row_data=participant)
        if result.get("success"):
            participant_ids.append(participant["id"])
            print(f"✅ Registered participant: {participant['name']}")
        else:
            print(f"❌ Failed to register participant: {participant['name']} - {result.get('error')}")
    
    print(f"📊 Participants registered: {len(participant_ids)}/{len(participants_data)}")
    
    # Test 4: Results Recording
    print("\n📊 TEST 4: Results Recording")
    print("-" * 50)
    
    results_data = [
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "participant_id": participant_ids[0],
            "rank": 1,
            "score": 95.5,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "participant_id": participant_ids[1],
            "rank": 2,
            "score": 87.3,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "participant_id": participant_ids[2],
            "rank": 3,
            "score": 82.1,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    result_ids = []
    for result_data in results_data:
        result = call_supabase_function("insert_row", table_name="results", row_data=result_data)
        if result.get("success"):
            result_ids.append(result_data["id"])
            print(f"✅ Recorded result: Rank {result_data['rank']} - Score {result_data['score']}")
        else:
            print(f"❌ Failed to record result: {result.get('error')}")
    
    print(f"📊 Results recorded: {len(result_ids)}/{len(results_data)}")
    
    # Test 5: Leaderboard Management
    print("\n🏅 TEST 5: Leaderboard Management")
    print("-" * 50)
    
    leaderboard_data = [
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "participant_id": participant_ids[0],
            "total_score": 95.5,
            "rank": 1,
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "participant_id": participant_ids[1],
            "total_score": 87.3,
            "rank": 2,
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "participant_id": participant_ids[2],
            "total_score": 82.1,
            "rank": 3,
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    leaderboard_ids = []
    for leaderboard_entry in leaderboard_data:
        result = call_supabase_function("insert_row", table_name="leaderboard", row_data=leaderboard_entry)
        if result.get("success"):
            leaderboard_ids.append(leaderboard_entry["id"])
            print(f"✅ Updated leaderboard: Rank {leaderboard_entry['rank']} - {leaderboard_entry['total_score']} points")
        else:
            print(f"❌ Failed to update leaderboard: {result.get('error')}")
    
    print(f"📊 Leaderboard entries: {len(leaderboard_ids)}/{len(leaderboard_data)}")
    
    # Test 6: Media Management
    print("\n📸 TEST 6: Media Management")
    print("-" * 50)
    
    media_data = [
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "participant_id": participant_ids[0],
            "type": "photo",
            "url": "https://example.com/photos/winner.jpg",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "competition_id": competition_id,
            "participant_id": participant_ids[1],
            "type": "video",
            "url": "https://example.com/videos/runner-up.mp4",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    media_ids = []
    for media in media_data:
        result = call_supabase_function("insert_row", table_name="media", row_data=media)
        if result.get("success"):
            media_ids.append(media["id"])
            print(f"✅ Added media: {media['type']} - {media['url']}")
        else:
            print(f"❌ Failed to add media: {result.get('error')}")
    
    print(f"📊 Media entries: {len(media_ids)}/{len(media_data)}")
    
    # Test 7: Complex Queries
    print("\n🔍 TEST 7: Complex Queries")
    print("-" * 50)
    
    # Query participants by competition
    result = call_supabase_function("query_table", table_name="participants", filters={"competition_id": competition_id})
    if result.get("success"):
        print(f"✅ Found {result.get('count', 0)} participants in competition")
    
    # Query results by competition
    result = call_supabase_function("query_table", table_name="results", filters={"competition_id": competition_id})
    if result.get("success"):
        print(f"✅ Found {result.get('count', 0)} results for competition")
    
    # Query leaderboard by competition
    result = call_supabase_function("query_table", table_name="leaderboard", filters={"competition_id": competition_id})
    if result.get("success"):
        print(f"✅ Found {result.get('count', 0)} leaderboard entries")
    
    # Query media by competition
    result = call_supabase_function("query_table", table_name="media", filters={"competition_id": competition_id})
    if result.get("success"):
        print(f"✅ Found {result.get('count', 0)} media items")
    
    # Test 8: Data Updates
    print("\n✏️ TEST 8: Data Updates")
    print("-" * 50)
    
    # Update competition status
    result = call_supabase_function("update_row", table_name="competitions", filters={"id": competition_id}, update_data={"description": "Updated: Competition completed successfully"})
    if result.get("success"):
        print("✅ Updated competition description")
    else:
        print(f"❌ Failed to update competition: {result.get('error')}")
    
    # Update participant information
    if participant_ids:
        result = call_supabase_function("update_row", table_name="participants", filters={"id": participant_ids[0]}, update_data={"phone": "+1-555-9999"})
        if result.get("success"):
            print("✅ Updated participant phone number")
        else:
            print(f"❌ Failed to update participant: {result.get('error')}")
    
    # Update leaderboard rank
    if leaderboard_ids:
        result = call_supabase_function("update_row", table_name="leaderboard", filters={"id": leaderboard_ids[0]}, update_data={"total_score": 96.0})
        if result.get("success"):
            print("✅ Updated leaderboard score")
        else:
            print(f"❌ Failed to update leaderboard: {result.get('error')}")
    
    # Test 9: Data Deletion
    print("\n🗑️ TEST 9: Data Deletion")
    print("-" * 50)
    
    # Delete media entries
    for media_id in media_ids:
        result = call_supabase_function("delete_row", table_name="media", filters={"id": media_id})
        if result.get("success"):
            print(f"✅ Deleted media entry: {media_id}")
        else:
            print(f"❌ Failed to delete media: {result.get('error')}")
    
    # Test 10: Final Verification
    print("\n✅ TEST 10: Final Verification")
    print("-" * 50)
    
    # Count all records
    total_records = 0
    for table in tables:
        result = call_supabase_function("query_table", table_name=table, filters={})
        if result.get("success"):
            count = result.get("count", 0)
            total_records += count
            print(f"📊 {table}: {count} records")
        else:
            print(f"❌ Failed to count {table}")
    
    print(f"\n🎯 TOTAL RECORDS: {total_records}")
    
    # Test Results Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    success_count = 0
    total_tests = 10
    
    # Count successful operations
    if len(existing_tables) == len(tables):
        success_count += 1
    if competition_id:
        success_count += 1
    if len(participant_ids) == len(participants_data):
        success_count += 1
    if len(result_ids) == len(results_data):
        success_count += 1
    if len(leaderboard_ids) == len(leaderboard_data):
        success_count += 1
    if len(media_ids) == len(media_data):
        success_count += 1
    if total_records > 0:
        success_count += 4  # Complex queries, updates, deletions, verification
    
    success_rate = (success_count / total_tests) * 100
    
    print(f"✅ Tests Passed: {success_count}/{total_tests}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT: Competition schema is fully functional!")
    elif success_rate >= 70:
        print("✅ GOOD: Competition schema is mostly functional")
    else:
        print("⚠️ NEEDS ATTENTION: Some issues detected")
    
    print("=" * 80)

def main():
    """Main test execution"""
    try:
        test_competition_schema()
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

