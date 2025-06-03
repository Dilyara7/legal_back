from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from legal_assistant.models import ChatDialog, ChatMessage
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from payment.models import Balance
from decimal import Decimal


class LegalAssistantTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("legal_assistant.views.OpenAI")
    def test_dialog_creation(self, mock_openai):
            # мок ответа от OpenAI
            mock_instance = MagicMock()
            mock_instance.responses.create.return_value.output_text = "Пример названия диалога"
            mock_openai.return_value = mock_instance

    def test_list_dialogs(self):
        ChatDialog.objects.create(user=self.user, name="Тестовый диалог")
        response = self.client.get("/dialogs/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) >= 1)
