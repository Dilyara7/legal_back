# serializers.py
from rest_framework import serializers
from .models import TemplateDocument

class TemplateDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateDocument
        fields = '__all__'
