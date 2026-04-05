from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from .models import Product, Category, CartItem, Order, OrderItem
from .forms import ProductForm, RegisterForm, LoginForm, OrderForm, AddToCartForm


def is_seller(user):
    """Check if user is a seller"""
    return user.is_authenticated and user.products.exists()


def is_superuser(user):
    """Check if user is superuser"""
    return user.is_authenticated and user.is_superuser


# ==================== Authentication Views ====================

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome!')
            return redirect('shop:home')
    else:
        form = RegisterForm()
    return render(request, 'shop/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop:home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('shop:home')
    else:
        form = LoginForm()
    return render(request, 'shop/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('shop:home')


# ==================== Product Views ====================

def home(request):
    """List all products with search and filter"""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': int(category_id) if category_id else None,
    }
    return render(request, 'shop/home.html', context)


def product_detail(request, pk):
    """View product details"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    form = AddToCartForm()
    context = {'product': product, 'form': form}
    return render(request, 'shop/product_detail.html', context)


# ==================== Seller Product Management (CRUD) ====================

@login_required
@user_passes_test(is_seller)
def seller_products(request):
    """List seller's products"""
    products = request.user.products.all()
    context = {'products': products}
    return render(request, 'shop/seller_products.html', context)


@login_required
def create_product(request):
    """Create a new product (seller only)"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('shop:seller_products')
    else:
        form = ProductForm()
    
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def update_product(request, pk):
    """Update product (seller only)"""
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('shop:seller_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@login_required
def delete_product(request, pk):
    """Delete product (seller only)"""
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('shop:seller_products')
    
    return render(request, 'shop/product_confirm_delete.html', {'product': product})


# ==================== Cart Views ====================

@login_required
def cart(request):
    """View shopping cart"""
    cart_items = request.user.cart_items.all()
    total_price = sum(item.total_price for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'shop/cart.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_cart(request, pk):
    """Add product to cart"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    form = AddToCartForm(request.POST)
    
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart!')
    
    return redirect('shop:cart')


@login_required
@require_http_methods(["POST"])
def remove_from_cart(request, pk):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('shop:cart')


@login_required
@require_http_methods(["POST"])
def update_cart_item(request, pk):
    """Update quantity in cart"""
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    quantity = request.POST.get('quantity', 1)
    
    try:
        quantity = int(quantity)
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
    except ValueError:
        messages.error(request, 'Invalid quantity!')
    
    return redirect('shop:cart')


# ==================== Order Views ====================

@login_required
def checkout(request):
    """Checkout - create order"""
    cart_items = request.user.cart_items.all()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('shop:home')
    
    total_price = sum(item.total_price for item in cart_items)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total_price
            
            # Set email from form or user
            if not order.email:
                order.email = request.user.email
            
            order.save()
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Clear cart
            cart_items.delete()
            
            messages.success(request, 'Order placed successfully!')
            return redirect('shop:order_detail', pk=order.pk)
    else:
        form = OrderForm(initial={'email': request.user.email})
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def orders(request):
    """List user's orders"""
    orders = request.user.orders.all()
    context = {'orders': orders}
    return render(request, 'shop/orders.html', context)


@login_required
def order_detail(request, pk):
    """Order details"""
    order = get_object_or_404(Order, pk=pk, user=request.user)
    items = order.items.all()
    context = {'order': order, 'items': items}
    return render(request, 'shop/order_detail.html', context)
