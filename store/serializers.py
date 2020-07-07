from rest_framework import serializers

from .models import Store, ServiceItem, StoreServiceItem


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class ServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceItem
        fields = '__all__'


class StoreServiceItemSerializer(serializers.ModelSerializer):
    service_item = ServiceItemSerializer(read_only=True, many=True)

    class Meta:
        model = StoreServiceItem
        fields = ('id', 'service_item')
