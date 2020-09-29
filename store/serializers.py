from datetime import datetime
from rest_framework import serializers

from .models import Store, ServiceItem, TableSeat


class TableSeatSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    timer = serializers.SerializerMethodField()
    last = serializers.SerializerMethodField()
    seated = serializers.SerializerMethodField()
    ordered = serializers.SerializerMethodField()

    class Meta:
        model = TableSeat
        fields = '__all__'

    def get_location(self, obj):
        return obj.location.title

    def get_timer(self, obj):
        if obj.last_time_status_changed:
            return int((datetime.now() - obj.last_time_status_changed).total_seconds())
        else:
            return 0

    def get_seated(self, obj):
        if obj.seated_time:
            return obj.seated_time.strftime("%H:%M %p")
        else:
            return ''

    def get_ordered(self, obj):
        if obj.ordered_time:
            return obj.ordered_time.strftime("%H:%M %p")
        else:
            return ''

    def get_last(self, obj):
        if obj.last_time_customer_tap:
            return int((datetime.now() - obj.last_time_customer_tap).total_seconds())
        else:
            return 0


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class ServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceItem
        fields = '__all__'
