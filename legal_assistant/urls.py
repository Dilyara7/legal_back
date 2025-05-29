# urls.py
from django.urls import path
from .views import chat_message_view,list_dialogs,delete_dialog,get_dialog
from .views import upload_template,list_templates,delete_template
from .views import *
urlpatterns = [
    path("", home, name="home"),
    path('chat/', chat_message_view, name='chat'),
    path('dialogs/', list_dialogs, name='dialogs'),
    path('dialogs/<str:dialog_id>/', get_dialog, name='get_dialog'),
    path('dialogs/<str:dialog_id>/delete/', delete_dialog, name='delete_dialog'),
    path('upload_template/', upload_template, name='upload_template'),
    path('templates/', list_templates, name='list_templates'),
    path('templates/<str:template_id>/delete/', delete_template, name='delete_template'),
]
