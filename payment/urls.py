# payment/urls.py
from django.urls import path
from .views import topup, balance, confirm_payment, webhook,transactions
from .serializers import BalanceSerialize  # теперь найдётся
app_name = 'payment'

urlpatterns = [
    path('topup/',       topup,           name='topup'),
    path('balance/',     balance,         name='balance'),
    path('confirm/',     confirm_payment, name='confirm'),
    path('webhook',     webhook,         name='webhook'),
    path('transactions/', transactions, name='transactions'),
]
