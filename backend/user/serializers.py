from rest_framework.serializers import ModelSerializer
from .models import Message, User

class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ['session', 'role', 'content', 'created_at']
        read_only_fields = ['created_at']

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'nickname']