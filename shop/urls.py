from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Products
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Seller Management (CRUD)
    path('seller/products/', views.seller_products, name='seller_products'),
    path('product/create/', views.create_product, name='create_product'),
    path('product/<int:pk>/edit/', views.update_product, name='update_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    
    # Cart
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    
    # Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
]
