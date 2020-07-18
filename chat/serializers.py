from rest_framework import serializers

from service.serializers import ServicemanSerializer
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    serviceman = ServicemanSerializer(read_only=True, many=False)

    class Meta:
        model = Message
        fields = '__all__'
