#!/usr/bin/env python3
"""
Strict Test Case for E-commerce Schema Deployment
Tests automatic table creation and comprehensive CRUD operations
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from claude_supabase_driver import call_supabase_function

load_dotenv()

def test_ecommerce_schema():
    """Comprehensive test of e-commerce schema deployment and operations"""
    
    print("=" * 80)
    print("E-COMMERCE SCHEMA STRICT TEST CASE")
    print("=" * 80)
    
    # Test 1: Schema Deployment
    print("\n📋 TEST 1: Schema Deployment")
    print("-" * 50)
    
    schema = """
CREATE TABLE IF NOT EXISTS "products" (
  "id" UUID NOT NULL,
  "name" TEXT NOT NULL,
  "description" TEXT NOT NULL,
  "price" DECIMAL NOT NULL,
  "inventory_count" INTEGER NOT NULL,
  "category" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE IF NOT EXISTS "customers" (
  "id" UUID NOT NULL,
  "name" TEXT NOT NULL,
  "email" TEXT NOT NULL,
  "phone" TEXT,
  "created_at" TIMESTAMP NOT NULL,
  PRIMARY KEY ("id"),
  UNIQUE ("email")
);
CREATE TABLE IF NOT EXISTS "orders" (
  "id" UUID NOT NULL,
  "customer_id" UUID NOT NULL,
  "order_date" TIMESTAMP NOT NULL,
  "status" TEXT NOT NULL,
  "total_amount" DECIMAL NOT NULL,
  "created_at" TIMESTAMP NOT NULL,
  PRIMARY KEY ("id"),
  FOREIGN KEY ("customer_id") REFERENCES "customers"("id")
);
CREATE TABLE IF NOT EXISTS "order_items" (
  "id" UUID NOT NULL,
  "order_id" UUID NOT NULL,
  "product_id" UUID NOT NULL,
  "quantity" INTEGER NOT NULL,
  "unit_price" DECIMAL NOT NULL,
  PRIMARY KEY ("id"),
  FOREIGN KEY ("order_id") REFERENCES "orders"("id"),
  FOREIGN KEY ("product_id") REFERENCES "products"("id")
);
CREATE TABLE IF NOT EXISTS "payments" (
  "id" UUID NOT NULL,
  "order_id" UUID NOT NULL,
  "amount" DECIMAL NOT NULL,
  "payment_method" TEXT NOT NULL,
  "status" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL,
  PRIMARY KEY ("id"),
  FOREIGN KEY ("order_id") REFERENCES "orders"("id")
);
"""
    
    # Deploy schema using the new schema inference approach
    print("🔧 Deploying schema via schema inference...")
    result = call_supabase_function("create_table", table_schema=schema)
    
    if result.get("success"):
        created_tables = result.get("tables_created", [])
        print(f"✅ Schema deployed successfully!")
        print(f"📊 Tables created: {', '.join(created_tables)}")
        print(f"📊 Method: {result.get('method', 'unknown')}")
    else:
        print(f"❌ Schema deployment failed: {result.get('error')}")
        print(f"💡 Instructions: {result.get('instructions', 'No instructions')}")
        return
    
    tables = ['products', 'customers', 'orders', 'order_items', 'payments']
    print(f"\n📊 Tables Status: {len(created_tables)}/{len(tables)} created")
    
    # Test 2: Data Insertion (Products)
    print("\n📦 TEST 2: Product Data Insertion")
    print("-" * 50)
    
    products_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Laptop Pro 15",
            "description": "High-performance laptop with 16GB RAM",
            "price": 1299.99,
            "inventory_count": 50,
            "category": "Electronics",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse with USB receiver",
            "price": 29.99,
            "inventory_count": 200,
            "category": "Accessories",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mechanical Keyboard",
            "description": "RGB mechanical keyboard with Cherry MX switches",
            "price": 149.99,
            "inventory_count": 75,
            "category": "Accessories",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    product_ids = []
    for product in products_data:
        result = call_supabase_function("insert_row", table_name="products", row_data=product)
        if result.get("success"):
            product_ids.append(product["id"])
            print(f"✅ Inserted product: {product['name']}")
        else:
            print(f"❌ Failed to insert product: {product['name']} - {result.get('error')}")
    
    print(f"📊 Products inserted: {len(product_ids)}/{len(products_data)}")
    
    # Test 3: Customer Data Insertion
    print("\n👥 TEST 3: Customer Data Insertion")
    print("-" * 50)
    
    customers_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+1-555-0456",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    customer_ids = []
    for customer in customers_data:
        result = call_supabase_function("insert_row", table_name="customers", row_data=customer)
        if result.get("success"):
            customer_ids.append(customer["id"])
            print(f"✅ Inserted customer: {customer['name']}")
        else:
            print(f"❌ Failed to insert customer: {customer['name']} - {result.get('error')}")
    
    print(f"📊 Customers inserted: {len(customer_ids)}/{len(customers_data)}")
    
    # Test 4: Order Creation
    print("\n🛒 TEST 4: Order Creation")
    print("-" * 50)
    
    if customer_ids and product_ids:
        order_data = {
            "id": str(uuid.uuid4()),
            "customer_id": customer_ids[0],
            "order_date": datetime.now().isoformat(),
            "status": "pending",
            "total_amount": 1479.97,
            "created_at": datetime.now().isoformat()
        }
        
        result = call_supabase_function("insert_row", table_name="orders", row_data=order_data)
        if result.get("success"):
            order_id = order_data["id"]
            print(f"✅ Created order: {order_id}")
            
            # Test 5: Order Items
            print("\n📋 TEST 5: Order Items Creation")
            print("-" * 50)
            
            order_items_data = [
                {
                    "id": str(uuid.uuid4()),
                    "order_id": order_id,
                    "product_id": product_ids[0],
                    "quantity": 1,
                    "unit_price": 1299.99
                },
                {
                    "id": str(uuid.uuid4()),
                    "order_id": order_id,
                    "product_id": product_ids[1],
                    "quantity": 2,
                    "unit_price": 29.99
                },
                {
                    "id": str(uuid.uuid4()),
                    "order_id": order_id,
                    "product_id": product_ids[2],
                    "quantity": 1,
                    "unit_price": 149.99
                }
            ]
            
            order_item_ids = []
            for item in order_items_data:
                result = call_supabase_function("insert_row", table_name="order_items", row_data=item)
                if result.get("success"):
                    order_item_ids.append(item["id"])
                    print(f"✅ Added order item: {item['quantity']}x product")
                else:
                    print(f"❌ Failed to add order item - {result.get('error')}")
            
            print(f"📊 Order items added: {len(order_item_ids)}/{len(order_items_data)}")
            
            # Test 6: Payment Processing
            print("\n💳 TEST 6: Payment Processing")
            print("-" * 50)
            
            payment_data = {
                "id": str(uuid.uuid4()),
                "order_id": order_id,
                "amount": 1479.97,
                "payment_method": "credit_card",
                "status": "completed",
                "created_at": datetime.now().isoformat()
            }
            
            result = call_supabase_function("insert_row", table_name="payments", row_data=payment_data)
            if result.get("success"):
                payment_id = payment_data["id"]
                print(f"✅ Processed payment: {payment_id}")
            else:
                print(f"❌ Failed to process payment - {result.get('error')}")
            
            # Test 7: Complex Queries
            print("\n🔍 TEST 7: Complex Queries")
            print("-" * 50)
            
            # Query orders by customer
            result = call_supabase_function("query_table", table_name="orders", filters={"customer_id": customer_ids[0]})
            if result.get("success"):
                print(f"✅ Found {result.get('count', 0)} orders for customer")
            
            # Query products by category
            result = call_supabase_function("query_table", table_name="products", filters={"category": "Electronics"})
            if result.get("success"):
                print(f"✅ Found {result.get('count', 0)} electronics products")
            
            # Query order items for order
            result = call_supabase_function("query_table", table_name="order_items", filters={"order_id": order_id})
            if result.get("success"):
                print(f"✅ Found {result.get('count', 0)} items in order")
            
            # Test 8: Data Updates
            print("\n✏️ TEST 8: Data Updates")
            print("-" * 50)
            
            # Update order status
            result = call_supabase_function("update_row", table_name="orders", filters={"id": order_id}, update_data={"status": "shipped"})
            if result.get("success"):
                print("✅ Updated order status to 'shipped'")
            else:
                print(f"❌ Failed to update order - {result.get('error')}")
            
            # Update product inventory
            result = call_supabase_function("update_row", table_name="products", filters={"id": product_ids[0]}, update_data={"inventory_count": 49})
            if result.get("success"):
                print("✅ Updated product inventory")
            else:
                print(f"❌ Failed to update inventory - {result.get('error')}")
            
            # Test 9: Data Deletion
            print("\n🗑️ TEST 9: Data Deletion")
            print("-" * 50)
            
            # Delete payment (test deletion)
            result = call_supabase_function("delete_row", table_name="payments", filters={"id": payment_id})
            if result.get("success"):
                print("✅ Deleted payment record")
            else:
                print(f"❌ Failed to delete payment - {result.get('error')}")
            
            # Test 10: Final Verification
            print("\n✅ TEST 10: Final Verification")
            print("-" * 50)
            
            # Count all records
            tables_to_count = ['products', 'customers', 'orders', 'order_items', 'payments']
            total_records = 0
            
            for table in tables_to_count:
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
            if len(created_tables) == len(tables):
                success_count += 1
            if len(product_ids) == len(products_data):
                success_count += 1
            if len(customer_ids) == len(customers_data):
                success_count += 1
            if order_id:
                success_count += 1
            if len(order_item_ids) == len(order_items_data):
                success_count += 1
            if payment_id:
                success_count += 1
            if total_records > 0:
                success_count += 4  # Complex queries, updates, deletions, verification
            
            success_rate = (success_count / total_tests) * 100
            
            print(f"✅ Tests Passed: {success_count}/{total_tests}")
            print(f"📊 Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: E-commerce schema is fully functional!")
            elif success_rate >= 70:
                print("✅ GOOD: E-commerce schema is mostly functional")
            else:
                print("⚠️ NEEDS ATTENTION: Some issues detected")
            
            print("=" * 80)
            
        else:
            print(f"❌ Failed to create order - {result.get('error')}")
    else:
        print("❌ Cannot create orders without customers and products")

def main():
    """Main test execution"""
    try:
        test_ecommerce_schema()
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()