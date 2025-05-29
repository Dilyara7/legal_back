from decimal import Decimal
import uuid

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from yookassa.client import ApiError
from yookassa import Configuration, Payment as YKPayment
from .models import Balance
from .serializers import BalanceSerialize, TransactionSerializer
from django.contrib.auth.models import User
from .models import Transaction
# sandbox-режим YooKassa
Configuration.debug   = True
Configuration.api_url    = 'https://api.yookassa.ru/v3/'
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

REQUEST_FEE = getattr(settings, 'REQUEST_FEE', Decimal('20.00'))

class PaymentRequired(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Недостаточно средств для выполнения запроса'
    default_code = 'payment_required'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def topup(request):
    # 2) Валидация суммы
    try:
        amount = Decimal(str(request.data['amount']))
    except (KeyError, ValueError):
        return Response({'error': 'Неверная сумма'}, status=status.HTTP_400_BAD_REQUEST)

    # 3) Пытаемся создать платёж
    try:
        idem_key = str(uuid.uuid4())
        payment = YKPayment.create({
            "idempotence_key": idem_key,
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": f"http://localhost:3000/profile/balance"
            },
            "capture": True,
            "description": request.data.get('description', ''),
            "metadata": {"user_id": str(request.user.id)}
        }, idem_key)

    except ApiError as e:
        # Ошибки от API YooKassa (unauthorized, bad_request и т.п.)
        body = {}
        if hasattr(e, 'raw_response') and e.raw_response is not None:
            try:
                body = e.raw_response.json()
            except:
                body = {'error': str(e)}
        else:
            body = {'error': str(e)}
        return Response(body, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Все остальные—for example network errors или SDK-бага
        return Response(
            {'error': 'Сервис платежей недоступен, попробуйте позже', 'details': str(e)},
            status=status.HTTP_502_BAD_GATEWAY
        )

    # 4) Успех
    return Response({
        "payment_id":          payment.id,
        "confirmation_url":    payment.confirmation.confirmation_url
    }, status=status.HTTP_201_CREATED)
    
    
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def balance(request):
    bal, _ = Balance.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        if bal.amount < REQUEST_FEE:
            raise PaymentRequired()
        bal.deduct(REQUEST_FEE)
    return Response({"balance": f"{bal.amount:.2f}"})

@api_view(['GET'])
@permission_classes([AllowAny])
def confirm_payment(request):
    pid = request.query_params.get('payment_id')
    status_q = request.query_params.get('status')
    if not pid or not status_q:
        return Response({'error': 'payment_id и status обязательны'}, status=status.HTTP_400_BAD_REQUEST)
    payment = YKPayment.fetch(pid)
    success = (payment.status == 'succeeded')
    new_bal = None
    if success:
        meta = payment.metadata or {}
        uid = meta.get('user_id')
        if uid:
            bal, _ = Balance.objects.get_or_create(user_id=uid)
            bal.top_up(Decimal(payment.amount.value))
            new_bal = bal.amount
    return Response({
        'success': success,
        'payment_id': payment.id,
        'new_balance': f"{new_bal:.2f}" if new_bal else None
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def webhook(request):
    """
    Обработка вебхуков от YooKassa.
    Сохраняет все платежные события в Transaction и обновляет баланс.
    """
    data = request.data
    event = data.get('event')             # e.g. "payment.succeeded"
    obj = data.get('object', {})          # тело объекта уведомления
    
    # Вытаскиваем общие поля
    tx_id   = obj.get('id')
    amt     = obj.get('amount', {})
    amount  = Decimal(amt.get('value', '0'))
    currency= amt.get('currency')
    description= obj.get('description', '')
    metadata= obj.get('metadata', {})     # содержит {'user_id': '...'}
    user_id = metadata.get('user_id')
    
    # Пытаемся найти пользователя (если указан)
    user = None
    if user_id:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            user = None
    
    # Сохраняем историю транзакции
    Transaction.objects.create(
        user           = user,
        transaction_id = tx_id,
        event          = event,
        amount         = amount,
        currency       = currency,
        description    = description,
        metadata       = metadata,
        raw            = data
    )
    
    # Обновляем баланс в зависимости от типа события
    if user:
        if event == Transaction.PAYMENT_SUCCEEDED:
            # успешное пополнение
            user.balance.top_up(amount)
        elif event == Transaction.REFUND_SUCCEEDED:
            # успешный возврат
            user.balance.deduct(amount)
        # остальные события (waiting_for_capture, canceled) не меняют баланс
    
    # Отвечаем YooKassa 200 OK
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactions(request):
    qs = request.user.transactions.all()
    serializer = TransactionSerializer(qs, many=True)
    print(serializer.data)
    return Response(serializer.data)