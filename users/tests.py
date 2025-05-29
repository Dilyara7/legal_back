from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class UserRegistrationTests(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'testuser2',
            'password': 'testpassword2',
            'email': 'testuser2@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('status', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_register_user_missing_field(self):
        url = reverse('register')
        data = {
            'username': 'testuser2',
            # 'password': 'testpassword2',
            'email': 'testuser2@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser2', password='testpassword2', email='testuser2@example.com')
        self.authenticate()

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    # def test_device_list(self):
    #     url = reverse('device-list')
    #     response = self.client.get(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertGreaterEqual(len(response.data), 1)

    

    # def test_unauthorized_device_list(self):
    #     self.client.credentials()  # Удаление токена для эмуляции неавторизованного запроса
    #     url = reverse('device-list')
    #     response = self.client.get(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
