from django.contrib import admin

from .models import UserProfile

admin.site.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'surname', 'name', 'patronymic', 'birthday')
    search_fields = ('user', 'phone', 'surname', 'name', 'patronymic', 'birthday')
    list_filter = ('user', 'phone', 'surname', 'name', 'patronymic', 'birthday')
    fields = ('user', 'phone', 'surname', 'name', 'patronymic', 'birthday')
    readonly_fields = ('user', 'phone', 'surname', 'name', 'patronymic', 'birthday')
    ordering = ('user')