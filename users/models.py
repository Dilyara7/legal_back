from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):#Модель профиля пользователя
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    additional_info = models.JSONField(blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    patronymic = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    telegram_username = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} Profile"


    # class Meta:
    #     verbose_name = 'User Profile'
    #     verbose_name_plural = 'User Profiles'
    # ordering = ['user']
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     # Здесь можно добавить дополнительную логику при сохранении профиля
    # def delete(self, *args, **kwargs):
    #     # Здесь можно добавить дополнительную логику при удалении профиля
    #     super().delete(*args, **kwargs)
    # def get_full_name(self):
    #     return f"{self.surname} {self.name} {self.patronymic}"
    # def get_age(self):
    #     from datetime import date
    #     if self.birthday:
    #         today = date.today()
    #         age = today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
    #         return age
    #     return None
    # def get_avatar_url(self):
    #     if self.avatar:
    #         return self.avatar.url
    #     return None
    # def get_additional_info(self):
    #     return self.additional_info if self.additional_info else {}


    