"""
Forms - store/forms.py
=======================
Forms handle user input (like login, signup, add product).
Django forms automatically validate the data.

VIVA TIP:
  - Django forms = HTML forms + validation in one
  - We define what fields are needed
  - Django checks if data is correct before saving
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


# ─────────────────────────────────────────
# SIGNUP FORM
# Used when a new user registers.
# Inherits from Django's built-in UserCreationForm
# which already includes password validation.
# ─────────────────────────────────────────
class SignupForm(UserCreationForm):
    # Extra field: email is required for signup
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User  # Use Django's built-in User model
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap CSS class to all fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


# ─────────────────────────────────────────
# LOGIN FORM
# Used when an existing user logs in.
# ─────────────────────────────────────────
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap CSS class to all fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


# ─────────────────────────────────────────
# PRODUCT FORM (Admin Only)
# Used by admin to add or edit products.
# This form stores data in MongoDB.
# ─────────────────────────────────────────
class ProductForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        label='Product Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., iPhone 15 Pro'
        })
    )
    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe the product...'
        })
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Price (₹)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 59999'
        })
    )
    category = forms.ChoiceField(
        choices=[
            ('Electronics', 'Electronics'),
            ('Clothing', 'Clothing'),
            ('Books', 'Books'),
            ('Home & Kitchen', 'Home & Kitchen'),
            ('Sports', 'Sports'),
            ('Other', 'Other'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    image_url = forms.URLField(
        required=False,
        label='Product Image URL',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Paste a link to an image (e.g. https://example.com/item.jpg)'
        })
    )
    stock = forms.IntegerField(
        initial=10,
        label='Stock Quantity',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 50'
        })
    )
