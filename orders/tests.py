from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from addresses.models import Address
from cart.models import Cart, CartItem
from products.models import Category, Inventory, Product
from .models import Order


User = get_user_model()


class OrderAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.category = Category.objects.create(
            name='Test Electronics'
        )

        self.product = Product.objects.create(
            category=self.category,
            name='Test Headphones',
            sku='TEST-1001',
            price=1000,
            stock=10,
            is_active=True
        )

        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity=10,
            reserved_quantity=0
        )

        self.address = Address.objects.create(
            user=self.user,
            address_type='home',
            full_name='Test User',
            phone_number='9876543210',
            address_line='Test Street',
            city='Vijayawada',
            state='Andhra Pradesh',
            postal_code='520001',
            is_default=True
        )

        self.cart = Cart.objects.create(
            user=self.user
        )

        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_create_order(self):
        response = self.client.post(
            '/api/orders/orders/',
            {
                'address_id': self.address.id
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['status'],
            'pending'
        )

        self.assertEqual(
            response.data['payment_status'],
            'pending'
        )

        self.assertEqual(
            response.data['total_amount'],
            '2000.00'
        )

        self.assertEqual(
            Order.objects.count(),
            1
        )

    def test_order_requires_address(self):
        response = self.client.post(
            '/api/orders/orders/',
            {},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_address(self):
        response = self.client.post(
            '/api/orders/orders/',
            {
                'address_id': 9999
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_order_reduces_inventory(self):
        response = self.client.post(
            '/api/orders/orders/',
            {
                'address_id': self.address.id
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.inventory.refresh_from_db()

        self.assertEqual(
            self.inventory.quantity,
            8
        )

    def test_customer_cannot_access_other_users_order(self):
        response = self.client.post(
            '/api/orders/orders/',
            {
                'address_id': self.address.id
            },
            format='json'
        )

        order_id = response.data['id']

        another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='testpassword123'
        )

        self.client.force_authenticate(
            user=another_user
        )

        response = self.client.get(
            f'/api/orders/orders/{order_id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )