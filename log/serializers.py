from rest_framework import serializers

from .models import CustomerLog, ServiceLog


class CustomerLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerLog
        fields = '__all__'


class ServiceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLog
        fields = '__all__'
