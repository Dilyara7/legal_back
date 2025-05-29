from django.contrib import admin
from .models import Balance, Transaction

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount')
    readonly_fields = ('user',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_id', 'event', 'amount', 'currency', 'created_at')
    readonly_fields = ('user', 'transaction_id', 'event', 'amount', 'currency', 'created_at')
    search_fields = ('transaction_id',)
    list_filter = ('event',)