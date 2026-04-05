"""
seed_products.py - Seed Sample Products into MongoDB
======================================================
Run this ONCE to add sample products to your store.

Command: python seed_products.py

This adds 10 realistic sample products across different categories.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from store.mongo_utils import get_products_collection

# ─────────────────────────────────────────────────────────
# Sample Products Data
# ─────────────────────────────────────────────────────────
SAMPLE_PRODUCTS = [
    {
        'name': 'Apple iPhone 15',
        'description': 'Latest Apple iPhone with A16 Bionic chip, 48MP camera, Dynamic Island feature, and USB-C connectivity. Available in multiple stunning colors.',
        'price': 79999.0,
        'category': 'Electronics',
        'image_url': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&h=400&fit=crop',
        'stock': 25,
    },
    {
        'name': 'Samsung Galaxy S24 Ultra',
        'description': 'Samsung flagship with S Pen support, 200MP camera, Snapdragon 8 Gen 3, and titanium build for premium feel and durability.',
        'price': 129999.0,
        'category': 'Electronics',
        'image_url': 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&h=400&fit=crop',
        'stock': 15,
    },
    {
        'name': 'Sony WH-1000XM5 Headphones',
        'description': 'Industry-leading noise cancelling wireless headphones with 30 hours battery life, exceptional sound quality, and comfortable over-ear design.',
        'price': 24999.0,
        'category': 'Electronics',
        'image_url': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400&h=400&fit=crop',
        'stock': 40,
    },
    {
        'name': 'Nike Air Max 270',
        'description': 'Stylish and comfortable everyday sneakers featuring Max Air unit in the heel for all-day cushioning. Lightweight mesh upper for breathability.',
        'price': 8999.0,
        'category': 'Sports',
        'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
        'stock': 60,
    },
    {
        'name': 'Python Programming (Automate the Boring Stuff)',
        'description': 'Best-selling book for learning Python programming from scratch. Practical projects, easy-to-follow examples, perfect for beginners and students.',
        'price': 599.0,
        'category': 'Books',
        'image_url': 'https://images.unsplash.com/photo-1550399105-c4db5fb85c18?w=400&h=400&fit=crop',
        'stock': 100,
    },
    {
        'name': 'Levi\'s Men\'s Slim Fit Jeans',
        'description': 'Classic slim fit denim jeans from Levi\'s. Made with high-quality denim for comfort and style. Suitable for casual and semi-formal occasions.',
        'price': 2499.0,
        'category': 'Clothing',
        'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop',
        'stock': 80,
    },
    {
        'name': 'Instant Pot Duo 7-in-1',
        'description': 'Multi-functional electric pressure cooker - replaces 7 kitchen appliances. Pressure cook, slow cook, rice cook, steam, sauté, and more.',
        'price': 8999.0,
        'category': 'Home & Kitchen',
        'image_url': 'https://images.unsplash.com/photo-1585515320310-259814833e62?w=400&h=400&fit=crop',
        'stock': 20,
    },
    {
        'name': 'MacBook Air M3',
        'description': 'Apple MacBook Air with M3 chip, 8GB RAM, 256GB SSD. Ultra-thin design, 18-hour battery life, stunning Liquid Retina display. Perfect for students.',
        'price': 114900.0,
        'category': 'Electronics',
        'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop',
        'stock': 10,
    },
    {
        'name': 'Yoga Mat Premium Non-Slip',
        'description': 'Extra thick 6mm yoga mat with excellent grip, sweat-proof surface, and carrying strap. Ideal for yoga, pilates, stretching and meditation.',
        'price': 1299.0,
        'category': 'Sports',
        'image_url': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&h=400&fit=crop',
        'stock': 50,
    },
    {
        'name': 'Uniqlo Round Neck T-Shirt',
        'description': 'Premium cotton Supima T-shirt from Uniqlo. Soft, breathable fabric that resists pilling and shrinking. Available in 20+ colors. Everyday essential.',
        'price': 999.0,
        'category': 'Clothing',
        'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop',
        'stock': 120,
    },
]


def seed():
    """Insert sample products into MongoDB."""
    products_col = get_products_collection()

    # Check if products already exist
    existing_count = products_col.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Database already has {existing_count} products.")
        choice = input("Do you want to add more? (y/n): ").strip().lower()
        if choice != 'y':
            print("Seeding cancelled.")
            return

    # Insert all sample products
    result = products_col.insert_many(SAMPLE_PRODUCTS)
    print(f"\n✅ Successfully added {len(result.inserted_ids)} products!")
    print("\nProducts added:")
    for i, p in enumerate(SAMPLE_PRODUCTS, 1):
        print(f"  {i}. {p['name']} — ₹{p['price']} [{p['category']}]")

    print("\n🎉 Your store is ready! Visit http://127.0.0.1:8000/ to see your products.")


if __name__ == '__main__':
    print("=" * 50)
    print("  ShopZone - Sample Product Seeder")
    print("=" * 50)
    seed()
