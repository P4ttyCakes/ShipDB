# 🚀 ShipDB Usage Examples

## 📊 **Basic Database Deployment**

### **Deploy via API**
```python
import requests

# Deploy a simple blog database
payload = {
    "project_id": "my_blog",
    "database_type": "dynamodb",
    "database_name": "blog_db",
    "schema_data": {
        "tables": [
            {"name": "posts", "primary_key": "post_id"},
            {"name": "comments", "primary_key": "comment_id"},
            {"name": "users", "primary_key": "user_id"}
        ]
    }
}

response = requests.post("http://localhost:8000/api/deploy/", json=payload)
print(response.json())
```

### **Direct Python Usage**
```python
import boto3
import asyncio
from app.services.deployment.dynamodb_service import DynamoDBService
from app.models.deployment import DeploymentRequest, DatabaseType

async def deploy_database():
    service = DynamoDBService()
    
    request = DeploymentRequest(
        project_id="my_project",
        database_type=DatabaseType.DYNAMODB,
        database_name="my_database",
        schema_data={
            "tables": [
                {"name": "users", "primary_key": "user_id"},
                {"name": "products", "primary_key": "product_id"}
            ]
        }
    )
    
    result = await service.deploy(request)
    print(f"Deployed: {result.deployment_id}")

# Run the deployment
asyncio.run(deploy_database())
```

## 🛒 **E-commerce Database Usage**

### **Add Products**
```python
import boto3

dynamodb = boto3.client('dynamodb', region_name='us-east-1')

# Add a product
dynamodb.put_item(
    TableName='ecommerce_store_products',
    Item={
        'product_id': {'S': 'prod_001'},
        'name': {'S': 'Wireless Headphones'},
        'price': {'N': '99.99'},
        'category_id': {'S': 'electronics'},
        'stock_quantity': {'N': '50'},
        'status': {'S': 'active'}
    }
)

# Get all products
response = dynamodb.scan(TableName='ecommerce_store_products')
for item in response['Items']:
    print(f"{item['name']['S']}: ${item['price']['N']}")
```

### **Create Orders**
```python
# Create an order
dynamodb.put_item(
    TableName='ecommerce_store_orders',
    Item={
        'order_id': {'S': 'order_001'},
        'user_id': {'S': 'user_001'},
        'total_amount': {'N': '199.98'},
        'status': {'S': 'pending'},
        'created_at': {'S': '2024-01-01T00:00:00Z'}
    }
)

# Add order items
dynamodb.put_item(
    TableName='ecommerce_store_order_items',
    Item={
        'order_item_id': {'S': 'item_001'},
        'order_id': {'S': 'order_001'},
        'product_id': {'S': 'prod_001'},
        'quantity': {'N': '2'},
        'unit_price': {'N': '99.99'},
        'total_price': {'N': '199.98'}
    }
)
```

## 📱 **Social Media Database Usage**

### **Create Users and Posts**
```python
# Create a user
dynamodb.put_item(
    TableName='social_platform_users',
    Item={
        'user_id': {'S': 'user_001'},
        'username': {'S': 'john_doe'},
        'email': {'S': 'john@example.com'},
        'display_name': {'S': 'John Doe'},
        'followers_count': {'N': '0'},
        'following_count': {'N': '0'}
    }
)

# Create a post
dynamodb.put_item(
    TableName='social_platform_posts',
    Item={
        'post_id': {'S': 'post_001'},
        'user_id': {'S': 'user_001'},
        'content': {'S': 'Just shipped my first app! 🚀'},
        'likes_count': {'N': '0'},
        'comments_count': {'N': '0'}
    }
)

# Like a post
dynamodb.put_item(
    TableName='social_platform_likes',
    Item={
        'like_id': {'S': 'like_001'},
        'post_id': {'S': 'post_001'},
        'user_id': {'S': 'user_002'},
        'created_at': {'S': '2024-01-01T00:00:00Z'}
    }
)
```

### **Social Interactions**
```python
# Follow a user
dynamodb.put_item(
    TableName='social_platform_follows',
    Item={
        'follow_id': {'S': 'follow_001'},
        'follower_id': {'S': 'user_002'},
        'following_id': {'S': 'user_001'},
        'created_at': {'S': '2024-01-01T00:00:00Z'}
    }
)

# Comment on a post
dynamodb.put_item(
    TableName='social_platform_comments',
    Item={
        'comment_id': {'S': 'comment_001'},
        'post_id': {'S': 'post_001'},
        'user_id': {'S': 'user_002'},
        'content': {'S': 'Congratulations! 🎉'},
        'likes_count': {'N': '0'}
    }
)
```

## 🔍 **Query Examples**

### **Get User's Posts**
```python
# Get all posts by a user
response = dynamodb.scan(
    TableName='social_platform_posts',
    FilterExpression='user_id = :user_id',
    ExpressionAttributeValues={':user_id': {'S': 'user_001'}}
)

for post in response['Items']:
    print(f"Post: {post['content']['S']}")
    print(f"Likes: {post['likes_count']['N']}")
```

### **Get Trending Posts**
```python
# Get all posts and sort by likes
response = dynamodb.scan(TableName='social_platform_posts')
posts = response['Items']

# Sort by likes count
trending = sorted(posts, key=lambda x: int(x['likes_count']['N']), reverse=True)

for post in trending[:5]:  # Top 5
    print(f"🔥 {post['content']['S']} - {post['likes_count']['N']} likes")
```

### **Get User's Orders**
```python
# Get orders for a specific user
response = dynamodb.scan(
    TableName='ecommerce_store_orders',
    FilterExpression='user_id = :user_id',
    ExpressionAttributeValues={':user_id': {'S': 'user_001'}}
)

for order in response['Items']:
    print(f"Order {order['order_id']['S']}: ${order['total_amount']['N']}")
```

## 🚀 **Running Demos**

### **Command Line Interface**
```bash
# Run the demo runner
python scripts/run_demos.py

# Or run specific demos
python scripts/demos/generate_ecommerce_database.py
python scripts/demos/generate_social_media_database.py
python scripts/demos/add_ecommerce_sample_data.py
```

### **Test Scripts**
```bash
# Run tests
python scripts/tests/test_aws_infrastructure.py
python scripts/tests/test_api.py
python scripts/tests/show_project_connection.py
```

## 📊 **Project Management**

### **List All Projects**
```python
import boto3

dynamodb = boto3.client('dynamodb', region_name='us-east-1')
response = dynamodb.list_tables()

# Group tables by project
projects = {}
for table_name in response['TableNames']:
    if 'ecommerce_store' in table_name:
        project = 'ecommerce_20241025_020803'
    elif 'social_platform' in table_name:
        project = 'social_media_20251025_023915'
    else:
        project = 'other'
    
    if project not in projects:
        projects[project] = []
    projects[project].append(table_name)

for project, tables in projects.items():
    print(f"Project: {project}")
    print(f"Tables: {len(tables)}")
    for table in tables:
        print(f"  • {table}")
```

## 💡 **Best Practices**

1. **Use Project IDs** - Always include unique project identifiers
2. **Consistent Naming** - Use clear, descriptive table names
3. **Primary Keys** - Always define primary keys for tables
4. **Environment Variables** - Store credentials securely
5. **Error Handling** - Always handle AWS API errors
6. **Resource Cleanup** - Delete unused resources to save costs

---

**Ready to build your applications!** 🚀
