from rest_framework import serializers


from .models import Serviceman
from store.serializers import StoreSerializer


class ServicemanSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    password = serializers.CharField(source='user.password', write_only=True)
    access_token = serializers.CharField(source='user.access_token', read_only=True)
    refresh_token = serializers.CharField(source='user.refresh_token', read_only=True)
    store = StoreSerializer(read_only=True, many=False)

    class Meta:
        model = Serviceman
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'password',
            'access_token',
            'refresh_token',
            'store'
        )
