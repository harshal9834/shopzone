"""
MongoDB Connection Utility
===========================
This file sets up the connection to MongoDB Atlas.
We use pymongo (Python driver for MongoDB).

HOW IT WORKS:
  1. Read MONGO_URI from .env file
  2. Create a MongoClient (like opening a door to the database)
  3. Select our database (ecommerce_db)
  4. Return collections (like tables in SQL)

VIVA TIP:
  - pymongo is Python's official MongoDB driver
  - MongoClient creates the connection
  - A collection in MongoDB = a table in SQL
  - A document in MongoDB = a row in SQL
"""

from pymongo import MongoClient
from django.conf import settings

# ─────────────────────────────────────────
# Create MongoDB Client
# This connects to MongoDB Atlas cloud
# ─────────────────────────────────────────
_client = None  # We store client here to reuse connection

def get_db():
    """
    Returns the MongoDB database.
    Uses singleton pattern - creates connection once, reuses it.
    """
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)  # Connect to Atlas
    return _client[settings.MONGO_DB_NAME]         # Return our database


def get_products_collection():
    """Returns the 'products' collection (like a table for products)."""
    return get_db()['products']


def get_cart_collection():
    """Returns the 'cart' collection (like a table for cart items)."""
    return get_db()['cart']


def get_profiles_collection():
    """Returns the 'user_profiles' collection."""
    return get_db()['user_profiles']


def get_addresses_collection():
    """Returns the 'addresses' collection."""
    return get_db()['addresses']


def get_orders_collection():
    """Returns the 'orders' collection."""
    return get_db()['orders']


def get_payments_collection():
    """Returns the 'payments' collection."""
    return get_db()['payments']


def get_tracking_collection():
    """Returns the 'tracking_logs' collection."""
    return get_db()['tracking_logs']
