from rest_framework import serializers
from .models import Balance
from .models import Transaction

class BalanceSerialize(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = ('user', 'amount')  # перечислите здесь нужные вам поля
        

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'transaction_id', 'event', 'amount', 'currency','description', 'created_at', 'metadata')
