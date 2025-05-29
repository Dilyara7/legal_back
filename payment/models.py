from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import uuid
from django.conf import settings
User = get_user_model()

class Balance(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='balance'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    expenses=models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    def top_up(self, value: Decimal):
        if value <= 0:
            raise ValidationError('Сумма пополнения должна быть положительной')
        self.amount += value
        self.save()

    def deduct(self, value: Decimal):
        if value <= 0:
            raise ValidationError('Сумма списания должна быть положительной')
        if self.amount < value:
            raise ValidationError('Недостаточно средств')
        self.expenses += value
        self.amount -= value
        self.save()

    def __str__(self):
        return f"{self.user.username}: {self.amount:.2f} KZT"
    
class Transaction(models.Model):
    PAYMENT_SUCCEEDED       = 'payment.succeeded'
    WAITING_FOR_CAPTURE     = 'payment.waiting_for_capture'
    PAYMENT_CANCELED        = 'payment.canceled'
    REFUND_SUCCEEDED        = 'refund.succeeded'
    PAYMENT_EVENTS = [
        (PAYMENT_SUCCEEDED,   'Успешный платёж'),
        (WAITING_FOR_CAPTURE, 'Ожидает подтверждения'),
        (PAYMENT_CANCELED,    'Отменён / ошибка'),
        (REFUND_SUCCEEDED,    'Успешный возврат'),
    ]

    user           = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='transactions')
    transaction_id = models.CharField(max_length=64)
    event          = models.CharField(max_length=32, choices=PAYMENT_EVENTS)
    amount         = models.DecimalField(max_digits=12, decimal_places=2)
    currency       = models.CharField(max_length=3)
    description    = models.CharField(max_length=64, blank=True, null=True)
    metadata       = models.JSONField(default=dict, blank=True)
    raw            = models.JSONField(default=dict, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
