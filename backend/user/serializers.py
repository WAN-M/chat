from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['session', 'role', 'content', 'created_at']
        read_only_fields = ['created_at']
