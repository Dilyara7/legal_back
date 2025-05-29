from django.contrib import admin
from legal_assistant.models import ChatDialog, ChatMessage, TemplateDocument
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model


admin.site.register(ChatDialog)
admin.site.register(ChatMessage)
admin.site.register(TemplateDocument)
