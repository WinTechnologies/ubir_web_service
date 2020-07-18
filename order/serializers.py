from rest_framework import serializers

from customer.serializers import CustomerSerializer
from store.serializers import StoreSerializer, ServiceItemSerializer
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True, many=False)
    store = StoreSerializer(read_only=True, many=False)
    service_item = ServiceItemSerializer(read_only=True, many=False)

    class Meta:
        model = Order
        fields = '__all__'
