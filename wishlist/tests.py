from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Product

from .models import WishlistItem


User = get_user_model()


class WishlistAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='wishuser',
            email='wish@example.com',
            password='testpassword123'
        )

        self.category = Category.objects.create(
            name='Wishlist Test Category'
        )

        self.product = Product.objects.create(
            category=self.category,
            name='Wishlist Test Product',
            sku='WISH-1001',
            price=2000,
            stock=10,
            is_active=True
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_add_product_to_wishlist(self):
        response = self.client.post(
            '/api/wishlist/',
            {
                'product': self.product.id
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            WishlistItem.objects.count(),
            1
        )

    def test_duplicate_wishlist_is_rejected(self):
        WishlistItem.objects.create(
            user=self.user,
            product=self.product
        )

        response = self.client.post(
            '/api/wishlist/',
            {
                'product': self.product.id
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_list_wishlist(self):
        WishlistItem.objects.create(
            user=self.user,
            product=self.product
        )

        response = self.client.get(
            '/api/wishlist/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_remove_from_wishlist(self):
        item = WishlistItem.objects.create(
            user=self.user,
            product=self.product
        )

        response = self.client.delete(
            f'/api/wishlist/{item.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertEqual(
            WishlistItem.objects.count(),
            0
        )

    def test_wishlist_requires_authentication(self):
        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            '/api/wishlist/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )