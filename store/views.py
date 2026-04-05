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
from .forms import SignupForm, LoginForm, ProductForm, UserProfileForm, AddressForm
from .mongo_utils import (
    get_products_collection, get_cart_collection, 
    get_profiles_collection, get_addresses_collection,
    get_orders_collection, get_payments_collection,
    get_tracking_collection
)
from django.conf import settings


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
@login_required
def add_to_cart(request, product_id):
    """
    Adds a product to the shopping cart.
    If product already in cart, increases quantity by 1.
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
            {'$inc': {'quantity': 1}}
        )
        messages.success(request, 'Quantity updated in cart!')
    else:
        # New product → add to cart
        cart_col.insert_one({
            'user_id': request.user.id,
            'product_id': product_id,
            'quantity': 1
        })
        messages.success(request, 'Product added to cart!')

    # Redirect back to previous page (Home, Search, Details) 
    # This solves the 'Add' problem of being kicked to the cart page
    next_url = request.META.get('HTTP_REFERER') or 'home'
    return redirect(next_url)


@login_required
def buy_now(request, product_id):
    """
    Adds a product to the shopping cart and redirects to checkout.
    """
    cart_col = get_cart_collection()

    # Check if existing in cart
    existing = cart_col.find_one({
        'user_id': request.user.id,
        'product_id': product_id
    })

    if existing:
        cart_col.update_one(
            {'_id': existing['_id']},
            {'$inc': {'quantity': 1}}
        )
    else:
        cart_col.insert_one({
            'user_id': request.user.id,
            'product_id': product_id,
            'quantity': 1
        })
    
    messages.success(request, 'Adding to purchase list...')
    return redirect('checkout')


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
# 🔄 UPDATE CART QUANTITY VIEW
# Updates the number of products wanted in the cart.
# VIVA: UPDATE operation (U in CRUD) — modifies 'quantity' field
# ══════════════════════════════════════════════════════════════
@login_required
def update_cart_quantity(request, cart_id):
    """
    Updates the quantity of an item in the cart.
    Accepts POST request with 'quantity'.
    """
    if request.method == 'POST':
        new_qty = int(request.POST.get('quantity', 1))
        
        if new_qty < 1:
            return redirect('remove_from_cart', cart_id=cart_id)
            
        cart_col = get_cart_collection()
        try:
            cart_col.update_one(
                {'_id': ObjectId(cart_id), 'user_id': request.user.id},
                {'$set': {'quantity': new_qty}}
            )
            messages.success(request, 'Cart updated!')
        except Exception:
            messages.error(request, 'Could not update quantity.')
            
    return redirect('cart')


# ══════════════════════════════════════════════════════════════
# 💳 CHECKOUT VIEW
# Simple checkout page (no payment gateway).
# VIVA: Clears the cart after order is "placed"
# ══════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════
# ✅ ORDER SUCCESS VIEW
# ══════════════════════════════════════════════════════════════
@login_required
def order_success(request):
    """Shows a success message after order is placed."""
    order_id = request.session.get('last_order_id')
    order = None
    if order_id:
        orders_col = get_orders_collection()
        order = orders_col.find_one({'_id': ObjectId(order_id)})
        # Enrich order ID for template link
        if order:
            order['id'] = str(order['_id'])
            
    return render(request, 'order_success.html', {'order': order})


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
            messages.success(request, f'Welcome, {user.username}! Account created successfully.')
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
                messages.success(request, f'Welcome back, {username}!')
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
    messages.info(request, 'You have been logged out. See you again!')
    return redirect('home')




# ══════════════════════════════════════════════════════════════
# 👤 PROFILE VIEWS
# ══════════════════════════════════════════════════════════════

@login_required
def complete_profile(request):
    """
    Forced profile completion page.
    Users cannot proceed to checkout without completing this.
    """
    profiles_col = get_profiles_collection()
    
    # Check if profile already exists
    existing = profiles_col.find_one({'user_id': request.user.id})
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile_data = {
                'user_id': request.user.id,
                'full_name': form.cleaned_data['full_name'],
                'phone_number': form.cleaned_data['phone_number'],
                'is_complete': True
            }
            profiles_col.update_one(
                {'user_id': request.user.id},
                {'$set': profile_data},
                upsert=True
            )
            messages.success(request, 'Profile updated successfully!')
            return redirect('home')
    else:
        initial_data = {}
        if existing:
            initial_data = {
                'full_name': existing.get('full_name', ''),
                'phone_number': existing.get('phone_number', '')
            }
        form = UserProfileForm(initial=initial_data)

    return render(request, 'complete_profile.html', {'form': form})


@login_required
def profile_view(request):
    """Shows user profile and addresses."""
    profiles_col = get_profiles_collection()
    addresses_col = get_addresses_collection()
    
    profile = profiles_col.find_one({'user_id': request.user.id})
    addresses = list(addresses_col.find({'user_id': request.user.id}))
    
    for addr in addresses:
        addr['id'] = str(addr['_id'])

    return render(request, 'profile.html', {
        'profile': profile,
        'addresses': addresses
    })


# ══════════════════════════════════════════════════════════════
# 📍 ADDRESS VIEWS
# ══════════════════════════════════════════════════════════════

@login_required
def address_list(request):
    """Lists all saved addresses for the user."""
    addresses_col = get_addresses_collection()
    addresses = list(addresses_col.find({'user_id': request.user.id}))
    for addr in addresses:
        addr['id'] = str(addr['_id'])
    return render(request, 'address_list.html', {'addresses': addresses})


@login_required
def add_address(request):
    """Add a new address with Google Maps integration."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            addresses_col = get_addresses_collection()
            
            # If this is marked as default, unset others
            if form.cleaned_data.get('is_default'):
                addresses_col.update_many(
                    {'user_id': request.user.id},
                    {'$set': {'is_default': False}}
                )
            
            address_data = {
                'user_id': request.user.id,
                'address_line': form.cleaned_data['address_line'],
                'city': form.cleaned_data['city'],
                'state': form.cleaned_data['state'],
                'country': form.cleaned_data['country'],
                'pincode': form.cleaned_data['pincode'],
                'latitude': form.cleaned_data.get('latitude'),
                'longitude': form.cleaned_data.get('longitude'),
                'is_default': form.cleaned_data.get('is_default', False)
            }
            addresses_col.insert_one(address_data)
            messages.success(request, 'Address added successfully! 📍')
            return redirect('address_list')
    else:
        form = AddressForm()
    
    return render(request, 'add_address.html', {
        'form': form,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    })


@login_required
def delete_address(request, address_id):
    """Delete a saved address."""
    addresses_col = get_addresses_collection()
    addresses_col.delete_one({'_id': ObjectId(address_id), 'user_id': request.user.id})
    messages.success(request, 'Address deleted! 🗑️')
    return redirect('address_list')


# ══════════════════════════════════════════════════════════════
# 💳 ADVANCED CHECKOUT & PAYMENTS
# ══════════════════════════════════════════════════════════════

import datetime
import random
import string

@login_required
def checkout(request):
    """
    Advanced Checkout.
    Step 1: Select Address
    Step 2: Review Order
    """
    cart_col = get_cart_collection()
    products_col = get_products_collection()
    addresses_col = get_addresses_collection()
    
    cart_items_raw = list(cart_col.find({'user_id': request.user.id}))
    if not cart_items_raw:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart')

    # Get user addresses
    addresses = list(addresses_col.find({'user_id': request.user.id}))
    for a in addresses:
        a['id'] = str(a['_id'])
    
    # Calculate totals
    total_price = 0
    items = []
    for item in cart_items_raw:
        product = products_col.find_one({'_id': ObjectId(item['product_id'])})
        if product:
            subtotal = float(product.get('price', 0)) * item.get('quantity', 1)
            total_price += subtotal
            items.append({
                'product_id': str(product['_id']),
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'subtotal': subtotal
            })

    delivery_charge = 40 if total_price < 500 else 0
    gst_amount = total_price * 0.18 # 18% GST Simulation
    final_total = total_price + delivery_charge + gst_amount
    est_delivery = datetime.date.today() + datetime.timedelta(days=3)

    if request.method == 'POST':
        address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method', 'upi') # Default to UPI
        
        if not address_id:
            messages.error(request, 'Please select a delivery address!')
        else:
            # Create Order in MongoDB
            orders_col = get_orders_collection()
            
            # Simplified Logic: Set payment status based on method
            payment_status = 'Pending'
            if payment_method == 'cod':
                payment_status = 'COD'
            
            order_data = {
                'user_id': request.user.id,
                'items': items,
                'total_amount': final_total,
                'delivery_charge': delivery_charge,
                'gst_amount': gst_amount,
                'address_id': address_id,
                'payment_method': payment_method,
                'status': 'Placed',
                'created_at': datetime.datetime.now(),
                'estimated_delivery': datetime.datetime.combine(est_delivery, datetime.time.min),
                'payment_status': payment_status
            }
            order_id = orders_col.insert_one(order_data).inserted_id
            
            # Store order ID in session for easy retrieval on success page if needed
            request.session['last_order_id'] = str(order_id)
            
            # Clear cart
            cart_col.delete_many({'user_id': request.user.id})
            
            if payment_method == 'cod':
                messages.success(request, 'Success! Your order has been placed.')
                return redirect('order_success')
            
            return redirect('payment_view', order_id=str(order_id))

    return render(request, 'checkout.html', {
        'addresses': addresses,
        'items': items,
        'total_price': total_price,
        'delivery_charge': delivery_charge,
        'gst_amount': gst_amount,
        'final_total': final_total,
        'est_delivery': est_delivery
    })


@login_required
def payment_view(request, order_id):
    """UPI Payment Simulation Page."""
    orders_col = get_orders_collection()
    order = orders_col.find_one({'_id': ObjectId(order_id)})
    
    # Generate Mock UPI URL
    # format: upi://pay?pa=shopzone@upi&pn=ShopZone&am=PRICE&cu=INR
    upi_id = "harshal@okaxis" # Simulation ID
    amount = order['total_amount']
    upi_url = f"upi://pay?pa={upi_id}&pn=ShopZone&am={amount:.2f}&cu=INR"
    
    # Generate a random transaction ID
    txn_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    return render(request, 'payment.html', {
        'order': order,
        'order_id': order_id,
        'upi_url': upi_url,
        'txn_id': txn_id
    })


@login_required
def payment_status(request, order_id):
    """Simulates the payment response from a gateway."""
    status = request.GET.get('status', 'failure')
    txn_id = request.GET.get('txn_id', 'N/A')
    
    orders_col = get_orders_collection()
    payments_col = get_payments_collection()
    tracking_col = get_tracking_collection()
    
    if status == 'success':
        # Update Order
        orders_col.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'payment_status': 'Success', 'txn_id': txn_id}}
        )
        # Create Payment Record
        payments_col.insert_one({
            'order_id': order_id,
            'txn_id': txn_id,
            'amount': orders_col.find_one({'_id': ObjectId(order_id)})['total_amount'],
            'status': 'Success',
            'timestamp': datetime.datetime.now()
        })
        # Add tracking log
        tracking_col.insert_one({
            'order_id': order_id,
            'status': 'Placed',
            'message': 'Order placed successfully and payment confirmed.',
            'timestamp': datetime.datetime.now()
        })
        messages.success(request, 'Payment Successful! Your order is being processed.')
        return redirect('order_success')
    else:
        messages.error(request, 'Payment Failed. Please try again.')
        return redirect('payment_view', order_id=order_id)


# ══════════════════════════════════════════════════════════════
# 📜 ORDER HISTORY & INVOICED
# ══════════════════════════════════════════════════════════════

@login_required
def order_history(request):
    """Show list of orders for the logged-in user."""
    orders_col = get_orders_collection()
    orders = list(orders_col.find({'user_id': request.user.id}).sort('created_at', -1))
    for o in orders:
        o['id'] = str(o['_id'])
    return render(request, 'order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Show order tracking and details."""
    orders_col = get_orders_collection()
    tracking_col = get_tracking_collection()
    addresses_col = get_addresses_collection()
    
    order = orders_col.find_one({'_id': ObjectId(order_id)})
    tracking_logs = list(tracking_col.find({'order_id': order_id}).sort('timestamp', -1))
    address = addresses_col.find_one({'_id': ObjectId(order['address_id'])})
    
    # Timeline stages
    stages = ['Placed', 'Packed', 'Shipped', 'Out for Delivery', 'Delivered']
    current_index = stages.index(order['status']) if order['status'] in stages else 0

    subtotal = float(order['total_amount']) - float(order['delivery_charge']) - float(order['gst_amount'])

    return render(request, 'order_detail.html', {
        'order': order,
        'order_id': order_id,
        'tracking_logs': tracking_logs,
        'address': address,
        'stages': stages,
        'current_index': current_index,
        'subtotal': subtotal
    })


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

@login_required
def download_invoice(request, order_id):
    """Generates a professional PDF invoice."""
    orders_col = get_orders_collection()
    order = orders_col.find_one({'_id': ObjectId(order_id)})
    
    # Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order_id}.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Logo / Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, height - 50, "SHOPZONE")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, "123 E-Commerce Lane, Digital City, India")
    p.drawString(50, height - 85, "GSTIN: 22AAAAA0000A1Z5")
    
    p.line(50, height - 100, width - 50, height - 100)
    
    # Invoice Info
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 130, "INVOICE")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 150, f"Order ID: {order_id}")
    p.drawString(50, height - 165, f"Date: {order['created_at'].strftime('%d-%m-%Y %H:%M')}")
    p.drawString(50, height - 180, f"Transaction ID: {order.get('txn_id', 'N/A')}")
    
    # Table Header
    y = height - 220
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Item Description")
    p.drawString(350, y, "Qty")
    p.drawString(400, y, "Price")
    p.drawString(500, y, "Total")
    p.line(50, y - 5, width - 50, y - 5)
    
    # Items
    p.setFont("Helvetica", 10)
    y -= 25
    for item in order['items']:
        p.drawString(50, y, item['name'])
        p.drawString(350, y, str(item['quantity']))
        p.drawString(400, y, f"n {item['price']}")
        p.drawString(500, y, f"n {item['subtotal']}")
        y -= 20
        if y < 100: # Simple overflow check
            p.showPage()
            y = height - 50
            
    p.line(350, y, width - 50, y)
    y -= 20
    p.drawString(400, y, "Subtotal:")
    p.drawString(500, y, f"n {order['total_amount'] - order['delivery_charge'] - order['gst_amount']}")
    y -= 15
    p.drawString(400, y, "Delivery:")
    p.drawString(500, y, f"n {order['delivery_charge']}")
    y -= 15
    p.drawString(400, y, "GST (18%):")
    p.drawString(500, y, f"n {order['gst_amount']}")
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y, "Grand Total:")
    p.drawString(500, y, f"n {order['total_amount']}")
    
    p.showPage()
    p.save()
    return response


# ══════════════════════════════════════════════════════════════
# 📊 PRO ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════

@login_required
def admin_dashboard(request):
    """Real-time Admin Analytics Dashboard."""
    if not request.user.is_staff:
        return redirect('home')
        
    orders_col = get_orders_collection()
    products_col = get_products_collection()
    profiles_col = get_profiles_collection()
    
    # Dashboard Stats
    total_revenue = list(orders_col.aggregate([
        {'$match': {'payment_status': 'Success'}},
        {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
    ]))
    revenue = total_revenue[0]['total'] if total_revenue else 0
    
    total_orders = orders_col.count_documents({})
    active_orders = orders_col.count_documents({'status': {'$ne': 'Delivered'}})
    total_users = profiles_col.count_documents({})
    
    # 7-Day Revenue Analytics (Aggregation)
    today = datetime.datetime.now()
    seven_days_ago = today - datetime.timedelta(days=7)
    
    pipeline = [
        {'$match': {
            'payment_status': 'Success',
            'created_at': {'$gte': seven_days_ago}
        }},
        {'$group': {
            '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at'}},
            'daily_total': {'$sum': '$total_amount'}
        }},
        {'$sort': {'_id': 1}}
    ]
    
    agg_result = list(orders_col.aggregate(pipeline))
    
    # Process for Chart.js (filling gaps with 0)
    chart_labels = []
    chart_data = []
    
    # Create map for fast lookup
    data_map = {item['_id']: item['daily_total'] for item in agg_result}
    
    for i in range(7):
        d = today - datetime.timedelta(days=6-i)
        date_str = d.strftime('%Y-%m-%d')
        label_str = d.strftime('%a, %d %b') # e.g., Sat, 05 Apr
        chart_labels.append(label_str)
        chart_data.append(data_map.get(date_str, 0))

    # Recent Orders
    recent_orders = list(orders_col.find().sort('created_at', -1).limit(5))
    for o in recent_orders:
        o['id'] = str(o['_id'])

    return render(request, 'admin_dashboard.html', {
        'revenue': revenue,
        'total_orders': total_orders,
        'active_orders': active_orders,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'chart_labels': chart_labels,
        'chart_data': chart_data
    })


@login_required
def admin_orders(request):
    """View and manage all orders."""
    if not request.user.is_staff:
        return redirect('home')
    orders_col = get_orders_collection()
    orders = list(orders_col.find().sort('created_at', -1))
    for o in orders:
        o['id'] = str(o['_id'])
    return render(request, 'admin_orders.html', {'orders': orders})


@login_required
def admin_update_order(request, order_id):
    """
    Update order status and add tracking log.
    Includes Carrier and Tracking ID for "proper" shipment management.
    """
    if not request.user.is_staff:
        return redirect('home')
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        carrier = request.POST.get('carrier', 'N/A')
        tracking_id = request.POST.get('tracking_id', 'N/A')
        message = request.POST.get('message', f'Order status updated to {new_status}')
        
        # Prepare custom message if it's empty
        if not message.strip():
            message = f'Package is currently {new_status.lower()}.'
            if new_status == 'Shipped':
                message = f'Your package has been shipped via {carrier}. Tracking Number: {tracking_id}'
        
        orders_col = get_orders_collection()
        tracking_col = get_tracking_collection()
        
        # Update current order state
        orders_col.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {
                'status': new_status,
                'carrier': carrier,
                'tracking_id': tracking_id,
            }}
        )
        
        # Log this state in the timeline
        tracking_col.insert_one({
            'order_id': order_id,
            'status': new_status,
            'carrier': carrier,
            'tracking_id': tracking_id,
            'message': message,
            'timestamp': datetime.datetime.now()
        })
        messages.success(request, f'Order #{order_id[:8]} updated to {new_status}!')
        
    return redirect('admin_orders')


@login_required
def admin_users(request):
    """List all registered users from profile collection."""
    if not request.user.is_staff:
        return redirect('home')
    profiles_col = get_profiles_collection()
    users = list(profiles_col.find())
    return render(request, 'admin_users.html', {'users': users})


# ─── PRODUCT MANAGEMENT (CRUD) ───────────────────────

@login_required
def admin_panel(request):
    """Admin Product list for management."""
    if not request.user.is_staff:
        return redirect('home')
    products_col = get_products_collection()
    products = list(products_col.find())
    for p in products:
        p['id'] = str(p['_id'])
    return render(request, 'admin_panel.html', {'products': products})


@login_required
def add_product(request):
    """Add a new product to MongoDB."""
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            products_col = get_products_collection()
            products_col.insert_one({
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
                'price': float(form.cleaned_data['price']),
                'category': form.cleaned_data['category'],
                'image_url': form.cleaned_data.get('image_url') or '/static/images/default-product.png',
                'stock': form.cleaned_data.get('stock', 0)
            })
            messages.success(request, 'Product added successfully! ✅')
            return redirect('admin_panel')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form, 'action': 'Add'})


@login_required
def edit_product(request, product_id):
    """Edit existing product."""
    if not request.user.is_staff:
        return redirect('home')
    products_col = get_products_collection()
    product = products_col.find_one({'_id': ObjectId(product_id)})
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            products_col.update_one(
                {'_id': ObjectId(product_id)},
                {'$set': {
                    'name': form.cleaned_data['name'],
                    'description': form.cleaned_data['description'],
                    'price': float(form.cleaned_data['price']),
                    'category': form.cleaned_data['category'],
                    'image_url': form.cleaned_data.get('image_url') or '/static/images/default-product.png',
                    'stock': form.cleaned_data.get('stock', 0)
                }}
            )
            messages.success(request, 'Product updated! ✅')
            return redirect('admin_panel')
    else:
        form = ProductForm(initial={
            'name': product['name'],
            'description': product['description'],
            'price': product['price'],
            'category': product['category'],
            'image_url': product.get('image_url', ''),
            'stock': product.get('stock', 0)
        })
    return render(request, 'add_product.html', {'form': form, 'action': 'Edit', 'product_id': product_id})


@login_required
def delete_product(request, product_id):
    """Delete product."""
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        products_col = get_products_collection()
        products_col.delete_one({'_id': ObjectId(product_id)})
        messages.success(request, 'Product deleted! 🗑️')
    return redirect('admin_panel')
