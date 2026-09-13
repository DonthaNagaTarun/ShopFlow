# ShopFlow 🛒

A backend-focused E-Commerce and Order Management REST API built with Django and Django REST Framework.

ShopFlow provides APIs for user authentication, product management, inventory tracking, shopping carts, wishlists, addresses, orders, payments, and product reviews.

## 🚀 Features

- 🔐 JWT-based authentication
- 👤 User registration and profile management
- 📦 Product and category management
- 📊 Inventory management
- 🛒 Shopping cart management
- ❤️ Wishlist management
- 📍 User address management
- 📋 Order creation and tracking
- 💳 Mock payment processing
- ⭐ Product reviews and ratings
- 🔄 Order status workflow
- 🔒 Role-based access control
- 📚 Swagger API documentation
- 🧪 Automated API tests
- ⚡ Pagination, filtering, searching and ordering

## 🛠️ Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- django-filter
- drf-spectacular
- SQLite
- Git & GitHub

## 📁 Project Structure

```text
ShopFlow/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── users/
├── products/
├── cart/
├── orders/
├── wishlist/
├── addresses/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md