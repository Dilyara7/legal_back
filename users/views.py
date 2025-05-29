from django.shortcuts import render

import requests
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from .models import UserProfile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')



@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(
            username=serializer.data['username'],
            password=serializer.data['password'],
            email=serializer.data['email']
        )
        profile=UserProfile.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'status': 'User registered successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            
        }, status=201)
    else:
        return Response(serializer.errors, status=401)


  

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user', 'phone', 'birthday','name','surname','patronymic','avatar','additional_info')
        
class UserProfileList(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            # этот метод возвращает профиль пользователя, если он есть
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        else:
            return Response({'error': 'User not found'}, status=404)

    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            # Обновление профиля пользователя
            data = request.data.copy()
            data['user'] = request.user.id
            
            serializer = UserProfileSerializer(profile, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except UserProfile.DoesNotExist:
            # создание профиля пользователя
            data = request.data.copy()
            data['user'] = request.user.id
            
            serializer = UserProfileSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Эндпоинт для получения и обновления профиля пользователя.
    """
    user = request.user
    profile = UserProfile.objects.get(user=user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=200)
    
    elif request.method == 'POST':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
#     else:
#         return Response({'error': 'Method not allowed'}, status=405)
#
#     return Response({'error': 'User not found'}, status=404)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_user_profile_avatar(request):
    """
    Эндпоинт для получения и обновления аватара пользователя.
    """
    user = request.user
    profile = UserProfile.objects.get(user=user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=200)
    
    elif request.method == 'POST':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_user(request):
    """
    Эндпоинт для получения и обновления профиля пользователя.
    """
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)
    
    elif request.method == 'POST':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
#     else:
#         return Response({'error': 'Method not allowed'}, status=405)
#
#     return Response({'error': 'User not found'}, status=404)
    
from legal_assistant.models import ChatDialog, ChatMessage, TemplateDocument
from payment.models import Balance,Transaction
from decimal import Decimal
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stats(request):
    """
    Эндпоинт для получения статистики пользователя.
    const stats = {
    totalConsultations: 12,
    completedConsultations: 10,
    totalSpent: 15750.0,
    currentBalance: userProfile?.balance || 2500.0,
  }
    """
    user = request.user
    profile = UserProfile.objects.get(user=user)
    total_consultations = ChatDialog.objects.filter(user=user).count()
    completed_consultations = ChatDialog.objects.filter(user=user).count()
    # total_spent = Transaction.objects.filter(user=user, event=Transaction.PAYMENT_SUCCEEDED).aggregate(total=models.Sum('amount'))['total'] or 0.0
    balance = Balance.objects.filter(user=user).first()
    total_spent=balance.expenses if balance else Decimal('0.00')
    current_balance=balance.amount if balance else Decimal('0.00')
   
    stats = {
        'totalConsultations': total_consultations,
        'completedConsultations': completed_consultations,
        'totalSpent': float(total_spent),
        'currentBalance': float(current_balance),
    }
    
    return Response(stats, status=200)