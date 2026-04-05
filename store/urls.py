"""
Store URL Configuration - store/urls.py
=========================================
This file maps URLs to view functions.

HOW IT WORKS (VIVA TIP):
  - When user visits /cart/, Django looks here
  - Finds path('cart/', views.cart_view, name='cart')
  - Calls the cart_view() function
  - Returns the cart.html page

URL PATTERNS EXPLAINED:
  /                   → home page (all products)
  /product/<id>/      → single product detail
  /cart/              → shopping cart
  /add/<id>/          → add product to cart
  /remove/<id>/       → remove from cart
  /checkout/          → checkout page
  /order-success/     → order confirmation
  /signup/            → user registration
  /login/             → user login
  /logout/            → user logout
  /admin-panel/       → admin product list
  /add-product/       → admin add product
  /edit-product/<id>/ → admin edit product
  /delete-product/<id>/ → admin delete product
"""

from django.urls import path
from . import views

# Removed app_name namespace to allow simple {% url 'home' %} in templates
# (Kept simple for Viva presentation)

urlpatterns = [
    # ─── USER PAGES ───────────────────────────────────────
    path('', views.home, name='home'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<str:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),

    # ─── AUTHENTICATION ───────────────────────────────────
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ─── ADMIN PANEL (CRUD) ───────────────────────────────
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<str:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<str:product_id>/', views.delete_product, name='delete_product'),
]
