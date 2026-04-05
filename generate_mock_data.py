import os
import django
import datetime
import random
from pymongo import MongoClient

# ⚙️ Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from store.mongo_utils import get_orders_collection, get_products_collection, get_profiles_collection

def generate_mock_data():
    print("🚀 Starting Mock Data Generation for ShopZone Dashboard...")
    
    orders_col = get_orders_collection()
    products_col = get_products_collection()
    profiles_col = get_profiles_collection()

    # 1. Clean existing mock orders (Optional, uncomment if you want a clean slate)
    # orders_col.delete_many({'is_mock': True})

    # 2. Get some real products to link to
    products = list(products_col.find().limit(5))
    if not products:
        print("❌ No products found in database. Please add some products first.")
        return

    # 3. Get or create a sample user profile
    profile = profiles_col.find_one()
    user_id = profile['user_id'] if profile else 1
    
    # 4. Generate orders for the last 7 days
    today = datetime.datetime.now()
    
    for i in range(14): # Generate 14 orders across last 7 days
        days_back = random.randint(0, 6)
        order_date = today - datetime.timedelta(days=days_back, hours=random.randint(0, 23))
        
        # Select 1-3 random items
        items = []
        total_price = 0
        for _ in range(random.randint(1, 3)):
            p = random.choice(products)
            qty = random.randint(1, 3)
            sub = float(p['price']) * qty
            total_price += sub
            items.append({
                'product_id': str(p['_id']),
                'name': p['name'],
                'price': p['price'],
                'quantity': qty,
                'subtotal': sub
            })
        
        gst = total_price * 0.18
        delivery = 50 if total_price < 1000 else 0
        final_total = total_price + gst + delivery

        order_doc = {
            'user_id': user_id,
            'items': items,
            'total_amount': final_total,
            'delivery_charge': delivery,
            'gst_amount': gst,
            'address_id': "mock_addr_id",
            'status': random.choice(['Placed', 'Packed', 'Shipped', 'Out for Delivery', 'Delivered']),
            'created_at': order_date,
            'payment_status': 'Success',
            'txn_id': f"MOCK_TXN_{random.randint(100000, 999999)}",
            'is_mock': True # Flag to identify mock data
        }
        
        orders_col.insert_one(order_doc)
    
    print("✅ Success! 14 Mock orders generated for the last 7 days.")
    print("📌 Refresh your Admin Dashboard to see the real-time graph.")

if __name__ == "__main__":
    generate_mock_data()
