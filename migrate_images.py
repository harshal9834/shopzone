import os
from pymongo import MongoClient
from bson import ObjectId
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

MONGO_URI = env('MONGO_URI', default='')
MONGO_DB_NAME = env('MONGO_DB_NAME', default='ecommerce_db')

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
products_col = db['products']

# Update all products that have no image_url or empty image_url
print("--- Migrating product image URLs ---")
query = {"$or": [{"image_url": ""}, {"image_url": None}, {"image_url": {"$exists": False}}]}
update = {"$set": {"image_url": "/static/images/default-product.png"}}

result = products_col.update_many(query, update)
print(f"Updated {result.modified_count} products.")
