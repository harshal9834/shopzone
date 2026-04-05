"""
Views - store/views.py
========================
Views are Python functions that handle web requests.
Each view does ONE specific job.

HOW VIEWS WORK (VIVA TIP):
  1. User visits a URL (e.g., /cart/)
  2. Django finds the matching view function
  3. View processes the request (gets data from DB, etc.)
  4. View returns an HTML page (HttpResponse)

FUNCTION-BASED VIEW STRUCTURE:
  def my_view(request):
      # 1. Get data from database
      # 2. Process logic
      # 3. Return rendered HTML template
      return render(request, 'template.html', {'data': data})
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from bson.objectid import ObjectId   # MongoDB uses ObjectId for primary keys
from bson.errors import InvalidId

from django.core.files.storage import FileSystemStorage
from .forms import SignupForm, LoginForm, ProductForm
from .mongo_utils import get_products_collection, get_cart_collection


# ══════════════════════════════════════════════════════════════
# 🏠 HOME VIEW
# Shows all products on the homepage.
# VIVA: This is a READ operation (R in CRUD)
# ══════════════════════════════════════════════════════════════
def home(request):
    """
    Home page - shows all available products.
    Fetches all documents from MongoDB 'products' collection.
    """
    products_col = get_products_collection()

    # Get search query from URL (e.g., /?search=phone)
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    # Build MongoDB query
    query = {}
    if search_query:
        # Case-insensitive search in name and description
        query['$or'] = [
            {'name': {'$regex': search_query, '$options': 'i'}},
            {'description': {'$regex': search_query, '$options': 'i'}},
        ]
    if category_filter:
        query['category'] = category_filter

    # Fetch products from MongoDB
    products = list(products_col.find(query))

    # Convert ObjectId to string so templates can use it
    # IMPORTANT: Rename '_id' to 'id' because Django templates
    # cannot access variables that start with underscore!
    for p in products:
        p['id'] = str(p['_id'])

    # Get cart count for the logged-in user
    cart_count = 0
    if request.user.is_authenticated:
        cart_col = get_cart_collection()
        cart_count = cart_col.count_documents({'user_id': request.user.id})

    # Get all categories for filter dropdown
    categories = products_col.distinct('category')

    context = {
        'products': products,
        'cart_count': cart_count,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
    }
    return render(request, 'home.html', context)


# ══════════════════════════════════════════════════════════════
# 📦 PRODUCT DETAIL VIEW
# Shows one product's full details.
# VIVA: Another READ operation
# ══════════════════════════════════════════════════════════════
def product_detail(request, product_id):
    """
    Product detail page - shows full info about one product.
    Uses MongoDB's ObjectId to find the specific product.
    """
    products_col = get_products_collection()

    try:
        # Find product by its MongoDB _id
        product = products_col.find_one({'_id': ObjectId(product_id)})
        if not product:
            messages.error(request, 'Product not found!')
            return redirect('home')
        # Rename '_id' to 'id' — Django templates CANNOT access underscore variables!
        product['id'] = str(product['_id'])
    except (InvalidId, Exception):
        messages.error(request, 'Invalid product ID!')
        return redirect('home')

    # Related products (same category, exclude current)
    related = list(products_col.find({
        'category': product.get('category', ''),
        '_id': {'$ne': ObjectId(product_id)}
    }).limit(4))
    for r in related:
        r['id'] = str(r['_id'])

    context = {
        'product': product,
        'related_products': related,
    }
    return render(request, 'product_detail.html', context)


# ══════════════════════════════════════════════════════════════
# 🛒 CART VIEW
# Shows all items in the user's cart.
# VIVA: READ operation for cart data
# ══════════════════════════════════════════════════════════════
@login_required  # User must be logged in to view cart
def cart_view(request):
    """
    Shopping cart page.
    Shows all products the user has added to their cart.
    @login_required means only logged-in users can see this.
    """
    cart_col = get_cart_collection()
    products_col = get_products_collection()

    # Get all cart items for this user
    cart_items_raw = list(cart_col.find({'user_id': request.user.id}))

    # Enrich cart items with product details from MongoDB
    cart_items = []
    total_price = 0

    for item in cart_items_raw:
        try:
            product = products_col.find_one({'_id': ObjectId(item['product_id'])})
            if product:
                product['id'] = str(product['_id'])  # Rename for template
                cart_items.append({
                    'cart_id': str(item['_id']),    # Cart record ID
                    'product': product,              # Full product details
                    'quantity': item.get('quantity', 1),
                    'subtotal': float(product.get('price', 0)) * item.get('quantity', 1)
                })
                total_price += float(product.get('price', 0)) * item.get('quantity', 1)
        except Exception:
            pass  # Skip invalid cart items

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': len(cart_items),
        'free_delivery_diff': max(0, 499 - total_price)
    }
    return render(request, 'cart.html', context)


# ══════════════════════════════════════════════════════════════
# ➕ ADD TO CART VIEW
# Adds a product to the user's cart.
# VIVA: CREATE operation (C in CRUD) — adds a cart document
# ══════════════════════════════════════════════════════════════
@login_required
def add_to_cart(request, product_id):
    """
    Adds a product to the shopping cart.
    If product already in cart, increases quantity by 1.
    Creates a new document in MongoDB 'cart' collection.
    """
    cart_col = get_cart_collection()

    # Check if product already exists in cart
    existing = cart_col.find_one({
        'user_id': request.user.id,
        'product_id': product_id
    })

    if existing:
        # Product already in cart → just increase quantity
        cart_col.update_one(
            {'_id': existing['_id']},
            {'$inc': {'quantity': 1}}  # $inc means increment
        )
        messages.success(request, 'Quantity updated in cart! 🛒')
    else:
        # New product → add to cart
        cart_col.insert_one({
            'user_id': request.user.id,
            'product_id': product_id,
            'quantity': 1
        })
        messages.success(request, 'Product added to cart! 🛒')

    return redirect('cart')


# ══════════════════════════════════════════════════════════════
# ❌ REMOVE FROM CART VIEW
# Removes a product from the user's cart.
# VIVA: DELETE operation (D in CRUD)
# ══════════════════════════════════════════════════════════════
@login_required
def remove_from_cart(request, cart_id):
    """
    Removes an item from the shopping cart.
    Deletes the document from MongoDB 'cart' collection.
    """
    cart_col = get_cart_collection()

    try:
        # Delete this cart item (only if it belongs to this user)
        cart_col.delete_one({
            '_id': ObjectId(cart_id),
            'user_id': request.user.id  # Security: can only remove own items
        })
        messages.success(request, 'Item removed from cart!')
    except Exception:
        messages.error(request, 'Could not remove item.')

    return redirect('cart')


# ══════════════════════════════════════════════════════════════
# 💳 CHECKOUT VIEW
# Simple checkout page (no payment gateway).
# VIVA: Clears the cart after order is "placed"
# ══════════════════════════════════════════════════════════════
@login_required
def checkout(request):
    """
    Checkout page.
    On GET: shows a form to enter delivery details.
    On POST: clears the cart and shows order confirmation.
    """
    cart_col = get_cart_collection()
    products_col = get_products_collection()

    # Calculate total for display
    cart_items_raw = list(cart_col.find({'user_id': request.user.id}))
    total_price = 0
    cart_items = []

    for item in cart_items_raw:
        try:
            product = products_col.find_one({'_id': ObjectId(item['product_id'])})
            if product:
                product['id'] = str(product['_id'])  # Rename for template
                subtotal = float(product.get('price', 0)) * item.get('quantity', 1)
                cart_items.append({
                    'product': product,
                    'quantity': item.get('quantity', 1),
                    'subtotal': subtotal
                })
                total_price += subtotal
        except Exception:
            pass

    if request.method == 'POST':
        # On form submission → "place" the order
        if not cart_items:
            messages.error(request, 'Your cart is empty!')
            return redirect('cart')

        # Clear the entire cart for this user
        cart_col.delete_many({'user_id': request.user.id})
        messages.success(request, '🎉 Order placed successfully! Thank you for shopping with us.')
        return redirect('order_success')

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'checkout.html', context)


# ══════════════════════════════════════════════════════════════
# ✅ ORDER SUCCESS VIEW
# ══════════════════════════════════════════════════════════════
@login_required
def order_success(request):
    """Shows a success message after order is placed."""
    return render(request, 'order_success.html')


# ══════════════════════════════════════════════════════════════
# 👤 SIGNUP VIEW
# Registers a new user.
# VIVA: Uses Django's built-in UserCreationForm
# ══════════════════════════════════════════════════════════════
def signup_view(request):
    """
    User Registration page.
    On GET: shows empty signup form.
    On POST: validates form data and creates new user.
    """
    if request.user.is_authenticated:
        return redirect('home')  # Already logged in → go home

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()           # Save user to database
            login(request, user)         # Automatically log them in
            messages.success(request, f'Welcome, {user.username}! Account created successfully. 🎉')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


# ══════════════════════════════════════════════════════════════
# 🔐 LOGIN VIEW
# Logs in an existing user.
# VIVA: authenticate() checks username+password, login() starts session
# ══════════════════════════════════════════════════════════════
def login_view(request):
    """
    User Login page.
    On GET: shows empty login form.
    On POST: authenticates user credentials and logs them in.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Create session for user
                messages.success(request, f'Welcome back, {username}! 👋')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm(request)

    return render(request, 'login.html', {'form': form})


# ══════════════════════════════════════════════════════════════
# 🚪 LOGOUT VIEW
# Logs out the current user.
# VIVA: Destroys the session so user is no longer authenticated
# ══════════════════════════════════════════════════════════════
def logout_view(request):
    """
    Logs out the user and redirects to home.
    logout() destroys the user's session cookie.
    """
    logout(request)
    messages.info(request, 'You have been logged out. See you again! 👋')
    return redirect('home')


# ══════════════════════════════════════════════════════════════
# 🔧 ADMIN PANEL - LIST PRODUCTS (Read)
# Shows all products to admin for management.
# VIVA: Only staff/superuser can access
# ══════════════════════════════════════════════════════════════
@login_required
def admin_panel(request):
    """
    Admin Panel - shows all products for management.
    Only accessible to admin (staff) users.
    """
    if not request.user.is_staff:
        messages.error(request, '🚫 Access denied! Admin only.')
        return redirect('home')

    products_col = get_products_collection()
    products = list(products_col.find())
    for p in products:
        p['id'] = str(p['_id'])  # Rename for template access

    context = {'products': products}
    return render(request, 'admin_panel.html', context)


# ══════════════════════════════════════════════════════════════
# ➕ ADD PRODUCT (Create)
# Admin adds a new product to MongoDB.
# VIVA: CREATE operation (C in CRUD)
# ══════════════════════════════════════════════════════════════
@login_required
def add_product(request):
    """
    Admin: Add a new product.
    On GET: shows empty product form.
    On POST: saves new product to MongoDB.
    CRUD: CREATE operation
    """
    if not request.user.is_staff:
        messages.error(request, '🚫 Access denied! Admin only.')
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            products_col = get_products_collection()

            # Handle Image Upload
            image_url = '/static/images/default-product.png'
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                fs = FileSystemStorage()
                filename = fs.save(f'products/{image_file.name}', image_file)
                image_url = fs.url(filename)

            # Create the product document for MongoDB
            product_data = {
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
                'price': float(form.cleaned_data['price']),
                'category': form.cleaned_data['category'],
                'image_url': image_url,
                'stock': form.cleaned_data['stock'],
            }

            products_col.insert_one(product_data)  # INSERT to MongoDB
            messages.success(request, f'✅ Product "{product_data["name"]}" added successfully!')
            return redirect('admin_panel')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form, 'action': 'Add'})


# ══════════════════════════════════════════════════════════════
# ✏️ EDIT PRODUCT (Update)
# Admin edits an existing product in MongoDB.
# VIVA: UPDATE operation (U in CRUD)
# ══════════════════════════════════════════════════════════════
@login_required
def edit_product(request, product_id):
    """
    Admin: Edit an existing product.
    On GET: shows form pre-filled with current product data.
    On POST: updates the product in MongoDB.
    CRUD: UPDATE operation
    """
    if not request.user.is_staff:
        messages.error(request, '🚫 Access denied! Admin only.')
        return redirect('home')

    products_col = get_products_collection()

    try:
        product = products_col.find_one({'_id': ObjectId(product_id)})
        if not product:
            messages.error(request, 'Product not found!')
            return redirect('admin_panel')
    except Exception:
        messages.error(request, 'Invalid product ID!')
        return redirect('admin_panel')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle photo update
            update_fields = {
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
                'price': float(form.cleaned_data['price']),
                'category': form.cleaned_data['category'],
                'stock': form.cleaned_data['stock'],
            }

            if 'image' in request.FILES:
                image_file = request.FILES['image']
                fs = FileSystemStorage()
                filename = fs.save(f'products/{image_file.name}', image_file)
                update_fields['image_url'] = fs.url(filename)
            elif not product.get('image_url'):
                # If no image uploaded AND no existing image, set default
                update_fields['image_url'] = '/static/images/default-product.png'

            # Update the document in MongoDB
            products_col.update_one(
                {'_id': ObjectId(product_id)}, 
                {'$set': update_fields}
            )
            messages.success(request, f'✅ Product updated successfully!')
            return redirect('admin_panel')
    else:
        # Pre-fill the form with existing product data
        form = ProductForm(initial={
            'name': product.get('name', ''),
            'description': product.get('description', ''),
            'price': product.get('price', 0),
            'category': product.get('category', 'Other'),
            'image_url': product.get('image_url', ''),
            'stock': product.get('stock', 0),
        })

    context = {
        'form': form,
        'product': product,
        'action': 'Edit',
        'product_id': product_id,
    }
    return render(request, 'add_product.html', context)


# ══════════════════════════════════════════════════════════════
# 🗑️ DELETE PRODUCT (Delete)
# Admin deletes a product from MongoDB.
# VIVA: DELETE operation (D in CRUD)
# ══════════════════════════════════════════════════════════════
@login_required
def delete_product(request, product_id):
    """
    Admin: Delete a product.
    Only allows POST requests (for security — no accidental deletion via link).
    CRUD: DELETE operation
    """
    if not request.user.is_staff:
        messages.error(request, '🚫 Access denied! Admin only.')
        return redirect('home')

    if request.method == 'POST':
        products_col = get_products_collection()
        try:
            result = products_col.delete_one({'_id': ObjectId(product_id)})
            if result.deleted_count:
                messages.success(request, '🗑️ Product deleted successfully!')
            else:
                messages.error(request, 'Product not found!')
        except Exception:
            messages.error(request, 'Error deleting product.')

    return redirect('admin_panel')
