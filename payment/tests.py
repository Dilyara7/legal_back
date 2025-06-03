from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from payment.models import Balance, Transaction
from unittest.mock import patch

class PaymentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_balance_initialization(self):
        response = self.client.get('/payment/balance/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('balance', response.data)
        self.assertEqual(response.data['balance'], '0.00')

    def test_deduct_with_insufficient_funds(self):
        response = self.client.post('/payment/balance/')
        self.assertEqual(response.status_code, 402)  # PAYMENT_REQUIRED

    def test_top_up_payment_creation_mocked(self):
        with patch('payment.views.YKPayment.create') as mock_create:
            mock_payment = type('obj', (object,), {
                'id': 'fake_id',
                'confirmation': type('obj', (object,), {'confirmation_url': 'http://example.com'})()
            })()
            mock_create.return_value = mock_payment

            response = self.client.post('/payment/topup/', {'amount': '5000.00'})
            self.assertEqual(response.status_code, 201)
            self.assertIn('confirmation_url', response.data)

    def test_transactions_list_empty(self):
        response = self.client.get('/payment/transactions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_balance_top_up_and_deduct_logic(self):
        balance, _ = Balance.objects.get_or_create(user=self.user)
        balance.top_up(Decimal('5000.00'))
        self.assertEqual(balance.amount, Decimal('5000.00'))

        balance.deduct(Decimal('1000.00'))
        self.assertEqual(balance.amount, Decimal('4000.00'))
        self.assertEqual(balance.expenses, Decimal('1000.00'))
