from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Address


User = get_user_model()


class AddressAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='addressuser',
            email='address@example.com',
            password='testpassword123'
        )

        self.client.force_authenticate(
            user=self.user
        )

    def create_address(self, is_default=False):
        return Address.objects.create(
            user=self.user,
            address_type='home',
            full_name='Test User',
            phone_number='9876543210',
            address_line='Test Street',
            city='Vijayawada',
            state='Andhra Pradesh',
            postal_code='520001',
            is_default=is_default
        )

    def test_create_address(self):
        response = self.client.post(
            '/api/addresses/',
            {
                'address_type': 'home',
                'full_name': 'Test User',
                'phone_number': '9876543210',
                'address_line': 'Test Street',
                'city': 'Vijayawada',
                'state': 'Andhra Pradesh',
                'postal_code': '520001',
                'is_default': True
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Address.objects.count(),
            1
        )

        self.assertTrue(
            Address.objects.first().is_default
        )

    def test_first_address_becomes_default(self):
        response = self.client.post(
            '/api/addresses/',
            {
                'address_type': 'home',
                'full_name': 'Test User',
                'phone_number': '9876543210',
                'address_line': 'Test Street',
                'city': 'Vijayawada',
                'state': 'Andhra Pradesh',
                'postal_code': '520001',
                'is_default': False
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Address.objects.first().is_default
        )

    def test_only_one_default_address(self):
        first = self.create_address(is_default=True)

        response = self.client.post(
            '/api/addresses/',
            {
                'address_type': 'work',
                'full_name': 'Test User',
                'phone_number': '9876543210',
                'address_line': 'Office Road',
                'city': 'Vijayawada',
                'state': 'Andhra Pradesh',
                'postal_code': '520002',
                'is_default': True
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        first.refresh_from_db()

        self.assertFalse(
            first.is_default
        )

        self.assertEqual(
            Address.objects.filter(
                user=self.user,
                is_default=True
            ).count(),
            1
        )

    def test_update_address(self):
        address = self.create_address(is_default=True)

        response = self.client.patch(
            f'/api/addresses/{address.id}/',
            {
                'city': 'Guntur'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        address.refresh_from_db()

        self.assertEqual(
            address.city,
            'Guntur'
        )

    def test_delete_address(self):
        address = self.create_address(is_default=True)

        response = self.client.delete(
            f'/api/addresses/{address.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertEqual(
            Address.objects.count(),
            0
        )

    def test_address_requires_authentication(self):
        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            '/api/addresses/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )