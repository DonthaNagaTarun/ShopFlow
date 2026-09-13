from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product, Review


User = get_user_model()


class ReviewAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewuser',
            email='review@example.com',
            password='testpassword123'
        )

        self.category = Category.objects.create(
            name='Review Test Category'
        )

        self.product = Product.objects.create(
            category=self.category,
            name='Review Test Product',
            sku='REV-1001',
            price=1000,
            stock=10,
            is_active=True
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_create_review(self):
        response = self.client.post(
            '/api/products/reviews/',
            {
                'product': self.product.id,
                'rating': 5,
                'comment': 'Excellent product!'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Review.objects.count(),
            1
        )

    def test_duplicate_review_is_rejected(self):
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Good product'
        )

        response = self.client.post(
            '/api/products/reviews/',
            {
                'product': self.product.id,
                'rating': 4,
                'comment': 'Another review'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_rating_is_rejected(self):
        response = self.client.post(
            '/api/products/reviews/',
            {
                'product': self.product.id,
                'rating': 6,
                'comment': 'Invalid rating'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_list_reviews(self):
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            comment='Very good'
        )

        response = self.client.get(
            '/api/products/reviews/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
        len(response.data['results']),
        1
    )

    def test_update_own_review(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=3,
            comment='Good'
        )

        response = self.client.patch(
            f'/api/products/reviews/{review.id}/',
            {
                'rating': 5,
                'comment': 'Excellent!'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        review.refresh_from_db()

        self.assertEqual(
            review.rating,
            5
        )

    def test_delete_own_review(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Excellent!'
        )

        response = self.client.delete(
            f'/api/products/reviews/{review.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertEqual(
            Review.objects.count(),
            0
        )

    def test_reviews_require_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            '/api/products/reviews/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )