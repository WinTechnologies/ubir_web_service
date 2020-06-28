from rest_framework import serializers


class BaseUserSerializer(serializers.Serializer):
    id = serializers.CharField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)
    access_token = serializers.CharField(source='user.access_token', read_only=True)
    refresh_token = serializers.CharField(source='user.refresh_token', read_only=True)

