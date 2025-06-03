from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from users.models import UserProfile
from payment.models import Balance
from decimal import Decimal
from rest_framework_simplejwt.tokens import RefreshToken

class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345678', email='test@example.com')
        self.profile = UserProfile.objects.create(user=self.user)
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)

    def test_get_user_profile(self):
        url = reverse('userprofile-list')
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)

    def test_update_user_profile(self):
        url = reverse('userprofile-list')
        data = {
            'phone': '+77001234567',
            'name': 'TestName'
        }
        response = self.client.post(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], '+77001234567')

    def test_get_user(self):
        url = reverse('user-details')
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_update_user(self):
        url = reverse('user-details')
        data = {'email': 'updated@example.com'}
        response = self.client.post(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_user_stats(self):
        # создадим баланс
        Balance.objects.filter(user=self.user).delete()
        Balance.objects.create(user=self.user, amount=Decimal('1500.00'), expenses=Decimal('250.00'))
        url = reverse('user-stats')
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totalConsultations', response.data)
        self.assertEqual(response.data['currentBalance'], 1500.00)
        self.assertEqual(response.data['totalSpent'], 250.00)
