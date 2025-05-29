from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),#API Получение токена
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),#API Обновление токена
    path('api/register', register_user, name='register'),#API Регистрация пользователя
    path('api/userprofile', get_user_profile, name='userprofile-list'),#API Данные пользователя и изменение
    path('api/userprofile/avatar/', get_user_profile_avatar, name='userprofile-list'),#API Данные пользователя и изменение
    path('api/user', get_user, name='user-details'),
    path('api/userstats/', get_stats, name='user-stats'),#API Статистика пользователя
]