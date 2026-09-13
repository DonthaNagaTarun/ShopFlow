from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Product, Inventory

from .models import Cart, CartItem


User = get_user_model()


class CartAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='cartuser',
            email='cart@example.com',
            password='testpassword123'
        )

        self.category = Category.objects.create(
            name='Cart Test Category'
        )

        self.product = Product.objects.create(
            category=self.category,
            name='Cart Test Product',
            sku='CART-1001',
            price=1500,
            stock=10,
            is_active=True
        )

        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity=10,
            reserved_quantity=0
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_add_product_to_cart(self):
        response = self.client.post(
            '/api/cart/cart/',
            {
                'product': self.product.id,
                'quantity': 2
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['item']['quantity'],
            2
        )

        self.assertEqual(
            CartItem.objects.count(),
            1
        )

    def test_add_same_product_increases_quantity(self):
        self.client.post(
            '/api/cart/cart/',
            {
                'product': self.product.id,
                'quantity': 2
            },
            format='json'
        )

        response = self.client.post(
            '/api/cart/cart/',
            {
                'product': self.product.id,
                'quantity': 3
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['item']['quantity'],
            5
        )

    def test_quantity_cannot_exceed_stock(self):
        response = self.client.post(
            '/api/cart/cart/',
            {
                'product': self.product.id,
                'quantity': 11
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_product(self):
        response = self.client.post(
            '/api/cart/cart/',
            {
                'product': 9999,
                'quantity': 1
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_update_cart_item(self):
        response = self.client.post(
            '/api/cart/cart/',
            {
                'product': self.product.id,
                'quantity': 2
            },
            format='json'
        )

        item_id = response.data['item']['id']

        response = self.client.patch(
            f'/api/cart/cart/{item_id}/',
            {
                'quantity': 5
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['quantity'],
            5
        )

    def test_delete_cart_item(self):
        response = self.client.post(
            '/api/cart/cart/',
            {
                'product': self.product.id,
                'quantity': 1
            },
            format='json'
        )

        item_id = response.data['item']['id']

        response = self.client.delete(
            f'/api/cart/cart/{item_id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertEqual(
            CartItem.objects.count(),
            0
        )

    def test_cart_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            '/api/cart/cart/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )