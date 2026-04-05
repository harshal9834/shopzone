"""
create_admin.py - Create Django Superuser (Admin)
==================================================
Run this to create an admin account.
Command: python create_admin.py

The admin can:
  - Access /admin-panel/ to manage products
  - Add, Edit, Delete products
  - Use CRUD operations
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from django.contrib.auth.models import User

# Admin credentials - change these!
ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@shopzone.com'
ADMIN_PASSWORD = 'admin123'  # Change this password!

def create_admin():
    if User.objects.filter(username=ADMIN_USERNAME).exists():
        print(f"⚠️  Admin '{ADMIN_USERNAME}' already exists!")
        print(f"   Login at: http://127.0.0.1:8000/login/")
        print(f"   Username: {ADMIN_USERNAME}")
        print(f"   Password: {ADMIN_PASSWORD}")
        return

    user = User.objects.create_superuser(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD
    )
    print("=" * 40)
    print("✅ Admin account created!")
    print("=" * 40)
    print(f"  URL:      http://127.0.0.1:8000/login/")
    print(f"  Username: {ADMIN_USERNAME}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print(f"  Panel:    http://127.0.0.1:8000/admin-panel/")
    print("=" * 40)
    print("⚠️  Change the password after first login!")

if __name__ == '__main__':
    create_admin()
