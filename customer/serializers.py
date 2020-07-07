from rest_framework import serializers
from customer.models import Customer, UBIRWiFi


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class UBIRWiFiSerializer(serializers.ModelSerializer):
    class Meta:
        model = UBIRWiFi
        fields = '__all__'
