"""
Main URL Configuration
=======================
This file connects URLs to views.
Think of it like a traffic director for your website.

URL Pattern:
  /            → home page
  /product/<id>→ product detail page
  /cart/       → shopping cart
  /add/<id>/   → add item to cart
  /remove/<id>/→ remove item from cart
  /checkout/   → checkout page
  /signup/     → register new user
  /login/      → user login
  /logout/     → user logout
  /admin-panel/→ admin product management
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin Panel (built-in)
    path('django-admin/', admin.site.urls),

    # All store URLs (defined in store/urls.py)
    path('', include('store.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
