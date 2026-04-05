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

print("--- Products in MongoDB ---")
for p in products_col.find():
    print(f"Name: {p.get('name')}")
    print(f"Image URL: {p.get('image_url')}")
    print("-" * 20)
