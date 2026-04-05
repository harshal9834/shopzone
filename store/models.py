"""
Models - store/models.py
=========================
In Django, models define the structure of data.
Since we use MongoDB (via pymongo), we don't need Django ORM models.
BUT we still need a simple Django model for the session/auth system.

NOTE FOR VIVA:
  - Django uses SQLite for its built-in User system
  - Our Product and Cart data is stored in MongoDB
  - This is a hybrid approach: Django Auth + MongoDB data storage

Models Explained:
-----------------
1. Product (stored in MongoDB):
   - name        → Name of the product (e.g., "iPhone 15")
   - description → Short description of the product
   - price       → Price in rupees (a number, e.g., 59999)
   - image_url   → URL/path to product image

2. Cart (stored in MongoDB):
   - user_id     → Which user added this item (Django User ID)
   - product_id  → Which product was added (MongoDB product _id)
   - quantity    → How many units in cart (default: 1)

IMPORTANT: We interact with these using pymongo, not Django ORM.
"""

# We don't need any Django models for MongoDB data.
# Django's built-in User model handles authentication.
# MongoDB collections are managed in mongo_utils.py and views.py.

# This file is intentionally minimal because:
# - Django auth (User, login, logout) uses SQLite via Django's built-in system
# - Product & Cart data use MongoDB via pymongo directly

# If you want to add extra fields to the user profile later,
# you could create a Profile model here connected to Django's User model.
