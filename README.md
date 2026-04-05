# 🛍️ E-Commerce Store - Django Mini Project

A fully functional E-Commerce application built with Django featuring product listings, user authentication, shopping cart, and order management.

## ✨ Features

### 👥 User Authentication
- User registration and login
- Seller accounts for product management
- User profiles and order history
- Secure password handling

### 📦 Product Management (CRUD)
- Create, Read, Update, Delete products
- Product categories
- Product images and descriptions
- Stock management
- Seller dashboard for product management

### 🛒 Shopping Cart
- Add/Remove products to cart
- Update quantities
- Cart persistence per user
- Real-time total calculation

### 📋 Orders & Checkout
- Checkout process with shipping details
- Order history tracking
- Order status management (Pending, Processing, Shipped, Delivered, Cancelled)
- Email and phone number capture

### 🔍 Product Search & Filter
- Search by product name/description
- Filter by category
- Active/Inactive product status

### 🛡️ Security
- CSRF protection on all forms
- SQL injection prevention with Django ORM
- Secure password hashing
- User permission checks

## 🏗️ Technology Stack

- **Backend:** Django 4.2
- **Database:** PostgreSQL (Supabase) / SQLite (local)
- **Frontend:** Bootstrap 5, HTML5, CSS3
- **File Storage:** Image uploads for products
- **Deployment:** Vercel ready

## 📁 Project Structure

```
ecommerce/
├── ecommerce/           # Main project settings
│   ├── settings.py     # Django configuration
│   ├── urls.py         # Main URL routing
│   └── wsgi.py         # WSGI application
├── shop/               # Main app
│   ├── models.py       # Database models
│   ├── views.py        # View logic
│   ├── forms.py        # Form classes
│   ├── admin.py        # Admin configuration
│   ├── urls.py         # App URL routing
│   └── migrations/     # Database migrations
├── templates/          # HTML templates
│   └── shop/
│       ├── base.html
│       ├── home.html
│       ├── login.html
│       ├── register.html
│       └── ...
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment

### Installation

1. **Clone and install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and set:
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url (optional for local SQLite)
```

3. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create superuser (admin):**
```bash
python manage.py createsuperuser
```

5. **Start development server:**
```bash
python manage.py runserver
```

6. **Access the application:**
   - Store: http://localhost:8000
   - Admin: http://localhost:8000/admin

## 📚 Database Models

### Product
- name, description, price, category
- stock, image, seller relationship
- created_at, updated_at, is_active

### Category
- name, description, slug
- unique_together: (name, slug)

### CartItem
- user, product, quantity
- unique_together: (user, product)

### Order
- user, status, total_price
- shipping_address, email, phone
- Statuses: pending, processing, shipped, delivered, cancelled

### OrderItem
- order, product, quantity, price
- Price stored at time of purchase

## 🎯 API Routes

### Authentication
- `POST /register/` - User registration
- `POST /login/` - User login
- `GET /logout/` - User logout

### Products
- `GET /` - Home page (all products)
- `GET /product/<id>/` - Product detail
- `GET /seller/products/` - Seller's products
- `POST /product/create/` - Create product
- `POST /product/<id>/edit/` - Update product
- `POST /product/<id>/delete/` - Delete product

### Cart
- `GET /cart/` - View cart
- `POST /cart/add/<id>/` - Add to cart
- `POST /cart/remove/<id>/` - Remove from cart
- `POST /cart/update/<id>/` - Update quantity

### Orders
- `POST /checkout/` - Create order
- `GET /orders/` - View orders
- `GET /order/<id>/` - Order details

## 🔐 User Permissions

- **Anonymous Users:** Can browse products
- **Registered Users:** Can add to cart, checkout, view orders
- **Sellers:** Can manage their own products
- **Admin:** Full access to all features

## 📝 Admin Features

- User management
- Product management with search and filters
- Order tracking and status updates
- Category management
- Cart item viewing

## 🌐 Deployment to Vercel

1. **Add environment variables in Vercel:**
   - DATABASE_URL (Supabase PostgreSQL)
   - SECRET_KEY
   - DEBUG=False

2. **Push to GitHub**

3. **Deploy from Vercel dashboard**

4. **Vercel will automatically:**
   - Install dependencies
   - Run migrations
   - Collect static files
   - Start the application

## 🛠️ Development Commands

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Django shell
python manage.py shell
```

## 📦 Dependencies

```
Django==4.2
Pillow==12.1.0          # Image handling
psycopg2-binary==2.9.9  # PostgreSQL adapter
dj-database-url==2.1.0  # Database URL parsing
python-dotenv==1.0.0    # Environment variables
gunicorn==21.2.0        # Production server
whitenoise==6.6.0       # Static files serving
```

## 🎨 Features Highlights

### Search & Filter
- Real-time product search
- Category-based filtering
- Combined search and filter

### Seller Features
- List all their products
- Create new products with images
- Edit product details
- Delete products
- Track product sales

### Checkout Experience
- Cart review before checkout
- Shipping address collection
- Contact information
- Order confirmation

### Order Management
- View order history
- Track order status
- View order items with prices
- Email and contact information

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Import Errors
```bash
pip install -r requirements.txt --force-reinstall
```

## 📞 Support & Updates

For issues or improvements, please create an issue or pull request.

---

**🎉 Ready to use! Customize and deploy with confidence.**

**Made with ❤️ using Django**
