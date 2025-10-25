#!/usr/bin/env python3
"""
Social Media Platform Database Generator
Creates a comprehensive social media database with all necessary tables
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "backend"))

from app.services.deployment.dynamodb_service import DynamoDBService
from app.models.deployment import DeploymentRequest, DatabaseType

def print_banner():
    print("📱" + "="*70 + "📱")
    print("📱" + " "*25 + "SOCIAL MEDIA PLATFORM GENERATOR" + " "*25 + "📱")
    print("📱" + " "*20 + "Complete Social Network Infrastructure" + " "*20 + "📱")
    print("📱" + "="*70 + "📱")
    print()

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * 60)

async def generate_social_media_database():
    print_banner()
    
    # Set environment variables
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    service = DynamoDBService()
    
    # Comprehensive Social Media Schema
    print_section("Social Media Platform Schema")
    
    social_media_schema = {
        "tables": [
            {
                "name": "users",
                "primary_key": "user_id",
                "description": "User profiles and account information"
            },
            {
                "name": "posts",
                "primary_key": "post_id",
                "description": "User posts and content"
            },
            {
                "name": "comments",
                "primary_key": "comment_id",
                "description": "Comments on posts"
            },
            {
                "name": "likes",
                "primary_key": "like_id",
                "description": "Likes on posts and comments"
            },
            {
                "name": "follows",
                "primary_key": "follow_id",
                "description": "User follow relationships"
            },
            {
                "name": "messages",
                "primary_key": "message_id",
                "description": "Direct messages between users"
            },
            {
                "name": "notifications",
                "primary_key": "notification_id",
                "description": "User notifications"
            },
            {
                "name": "stories",
                "primary_key": "story_id",
                "description": "Temporary stories (24-hour content)"
            },
            {
                "name": "groups",
                "primary_key": "group_id",
                "description": "User groups and communities"
            },
            {
                "name": "group_members",
                "primary_key": "membership_id",
                "description": "Group membership relationships"
            },
            {
                "name": "hashtags",
                "primary_key": "hashtag_id",
                "description": "Hashtag tracking and trending"
            },
            {
                "name": "media",
                "primary_key": "media_id",
                "description": "Images, videos, and other media files"
            }
        ]
    }
    
    print("📱 Complete Social Media Platform Structure:")
    print(json.dumps(social_media_schema, indent=2))
    
    # Deploy the database
    print_section("Deploying Social Media Database to AWS")
    print("☁️  Creating comprehensive social media infrastructure...")
    
    request = DeploymentRequest(
        project_id=f"social_media_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        database_type=DatabaseType.DYNAMODB,
        database_name="social_platform",
        schema_data=social_media_schema
    )
    
    try:
        result = await service.deploy(request)
        print("✅ Social media database deployed successfully!")
        print()
        
        # Show results
        print_section("Deployment Results")
        print(f"🎯 Deployment ID: {result.deployment_id}")
        print(f"📊 Status: {result.status}")
        print(f"🌍 Region: {result.connection_info['region']}")
        print(f"📋 Tables Created: {len(result.connection_info['tables'])}")
        print()
        
        print("📋 Social Media Tables Created:")
        for i, table in enumerate(result.connection_info['tables'], 1):
            print(f"   {i:2d}. {table}")
        print()
        
        # Show connection info
        print_section("Database Connection Information")
        print("🔗 Your social media database is ready!")
        print()
        print("📝 AWS Credentials:")
        print(f"   Access Key ID: {result.connection_info['access_key_id']}")
        print(f"   Secret Key: {result.connection_info['secret_access_key'][:8]}...")
        print(f"   Region: {result.connection_info['region']}")
        print()
        
        # Show sample data structure
        print_section("Sample Data Structure")
        print("📊 Here's how to structure your social media data:")
        print()
        
        sample_data = {
            "users": {
                "user_id": "user_001",
                "username": "john_doe",
                "email": "john@example.com",
                "display_name": "John Doe",
                "bio": "Software developer and coffee enthusiast",
                "followers_count": 150,
                "following_count": 75,
                "created_at": "2024-01-01T00:00:00Z"
            },
            "posts": {
                "post_id": "post_001",
                "user_id": "user_001",
                "content": "Just shipped my first app! 🚀 #coding #success",
                "likes_count": 25,
                "comments_count": 5,
                "created_at": "2024-01-01T12:00:00Z",
                "media_urls": ["https://example.com/image1.jpg"]
            },
            "comments": {
                "comment_id": "comment_001",
                "post_id": "post_001",
                "user_id": "user_002",
                "content": "Congratulations! That's amazing! 🎉",
                "likes_count": 3,
                "created_at": "2024-01-01T12:15:00Z"
            },
            "follows": {
                "follow_id": "follow_001",
                "follower_id": "user_002",
                "following_id": "user_001",
                "created_at": "2024-01-01T10:00:00Z"
            }
        }
        
        print("📝 Sample Data Examples:")
        for table, data in sample_data.items():
            print(f"\n🔹 {table.upper()} Table:")
            print(json.dumps(data, indent=4))
        
        # Show Python usage
        print_section("Python Usage Examples")
        print("🐍 How to use your social media database:")
        print()
        
        python_code = '''
import boto3
import json

# Connect to your social media database
dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id='your_aws_access_key',
    aws_secret_access_key='your_aws_secret_key',
    region_name='us-east-1'
)

# Create a new user
def create_user(user_id, username, email, display_name):
    dynamodb.put_item(
        TableName='social_platform_users',
        Item={
            'user_id': {'S': user_id},
            'username': {'S': username},
            'email': {'S': email},
            'display_name': {'S': display_name},
            'followers_count': {'N': '0'},
            'following_count': {'N': '0'},
            'created_at': {'S': '2024-01-01T00:00:00Z'}
        }
    )

# Create a post
def create_post(post_id, user_id, content):
    dynamodb.put_item(
        TableName='social_platform_posts',
        Item={
            'post_id': {'S': post_id},
            'user_id': {'S': user_id},
            'content': {'S': content},
            'likes_count': {'N': '0'},
            'comments_count': {'N': '0'},
            'created_at': {'S': '2024-01-01T00:00:00Z'}
        }
    )

# Like a post
def like_post(like_id, post_id, user_id):
    dynamodb.put_item(
        TableName='social_platform_likes',
        Item={
            'like_id': {'S': like_id},
            'post_id': {'S': post_id},
            'user_id': {'S': user_id},
            'created_at': {'S': '2024-01-01T00:00:00Z'}
        }
    )

# Follow a user
def follow_user(follow_id, follower_id, following_id):
    dynamodb.put_item(
        TableName='social_platform_follows',
        Item={
            'follow_id': {'S': follow_id},
            'follower_id': {'S': follower_id},
            'following_id': {'S': following_id},
            'created_at': {'S': '2024-01-01T00:00:00Z'}
        }
    )

# Get user's posts
def get_user_posts(user_id):
    response = dynamodb.scan(
        TableName='social_platform_posts',
        FilterExpression='user_id = :user_id',
        ExpressionAttributeValues={':user_id': {'S': user_id}}
    )
    return response['Items']

# Get trending posts
def get_trending_posts():
    response = dynamodb.scan(TableName='social_platform_posts')
    posts = response['Items']
    # Sort by likes_count (simplified)
    return sorted(posts, key=lambda x: int(x['likes_count']['N']), reverse=True)
'''
        
        print("```python")
        print(python_code)
        print("```")
        
        # Show business logic examples
        print_section("Social Media Business Logic")
        print("💼 Common social media operations:")
        print()
        print("👥 User Management:")
        print("   • User registration and profiles")
        print("   • Follow/unfollow users")
        print("   • User search and discovery")
        print("   • Profile customization")
        print()
        print("📝 Content Management:")
        print("   • Create and edit posts")
        print("   • Upload media (images/videos)")
        print("   • Use hashtags and mentions")
        print("   • Story creation (24-hour content)")
        print()
        print("💬 Social Interactions:")
        print("   • Like and unlike posts")
        print("   • Comment on posts")
        print("   • Share posts")
        print("   • Direct messaging")
        print()
        print("🔔 Notifications:")
        print("   • New follower notifications")
        print("   • Like and comment notifications")
        print("   • Message notifications")
        print("   • Trending content alerts")
        print()
        print("📊 Analytics:")
        print("   • Post engagement metrics")
        print("   • User growth tracking")
        print("   • Trending hashtags")
        print("   • Content performance")
        
        # Verify in AWS
        print_section("AWS Verification")
        print("🔍 Verifying tables in AWS DynamoDB...")
        
        import boto3
        client = boto3.client('dynamodb', region_name='us-east-1')
        tables = client.list_tables()
        
        social_tables = [t for t in tables['TableNames'] if 'social_platform' in t]
        
        print(f"✅ Found {len(social_tables)} social media tables in AWS:")
        for table in sorted(social_tables):
            print(f"   🎯 {table}")
        
        print(f"\n📊 Total tables in AWS: {len(tables['TableNames'])}")
        
        # Show project comparison
        print_section("Project Comparison")
        print("🔄 Now you have TWO separate projects:")
        print()
        print("🛒 E-commerce Project:")
        print("   • Project ID: ecommerce_20241025_020803")
        print("   • Database: ecommerce_store")
        print("   • Tables: 12 (users, products, orders, etc.)")
        print("   • Purpose: Online store functionality")
        print()
        print("📱 Social Media Project:")
        print(f"   • Project ID: {request.project_id}")
        print("   • Database: social_platform")
        print("   • Tables: 12 (users, posts, comments, etc.)")
        print("   • Purpose: Social networking functionality")
        print()
        print("✅ Both projects are completely independent!")
        print("   • Different table names")
        print("   • Different project IDs")
        print("   • Different purposes")
        print("   • Can be managed separately")
        
        # Final summary
        print_section("Social Media Database Complete!")
        print("🎉 Your complete social media database is ready!")
        print()
        print("✅ What you have:")
        print(f"   • {len(social_tables)} database tables")
        print("   • Complete user management")
        print("   • Post and content system")
        print("   • Social interactions (likes, comments)")
        print("   • Follow system")
        print("   • Direct messaging")
        print("   • Notifications system")
        print("   • Stories functionality")
        print("   • Groups and communities")
        print("   • Hashtag tracking")
        print("   • Media management")
        print()
        print("🚀 Ready for:")
        print("   • Social media app development")
        print("   • Community platform")
        print("   • Content sharing platform")
        print("   • Messaging app")
        print("   • Group collaboration tool")
        print()
        print("💡 Next steps:")
        print("   1. Add sample users and posts")
        print("   2. Build your social media frontend")
        print("   3. Implement real-time notifications")
        print("   4. Add media upload functionality")
        print("   5. Create user discovery features")
        
        return result
        
    except Exception as e:
        print(f"❌ Social media database deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(generate_social_media_database())
