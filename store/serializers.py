import pytz
from datetime import datetime
from rest_framework import serializers

from .models import Store, ServiceItem, TableSeat
from customer.models import Customer
from .utils import rchop

class TableSeatSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    timer = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    record_number = serializers.SerializerMethodField()
    seated_time = serializers.SerializerMethodField()
    ordered = serializers.SerializerMethodField()
    seated = serializers.SerializerMethodField()

    class Meta:
        model = TableSeat
        fields = '__all__'

    def get_location(self, obj):
        return obj.location.title

    def get_timer(self, obj):
        store_id = rchop(obj.table_id, "." + obj.table_seat)
        store = Store.objects.get(store_id=store_id)
        if obj.last_time_status_changed:
            return int((datetime.now(pytz.timezone(store.timezone)) - obj.last_time_status_changed).total_seconds())
        else:
            return 0

    def get_seated_time(self, obj):
        if obj.seated_time:
            return obj.seated_time.strftime("%H:%M %p")
        else:
            return ''

    def get_ordered(self, obj):
        if obj.ordered_time:
            return obj.ordered_time.strftime("%H:%M %p")
        else:
            return ''

    def get_last_name(self, obj):
        try:
            customer = Customer.objects.get(store_id=rchop(obj.table_id, "." + obj.table_seat), table_id='wait_list',
                                            assigned_table_id=obj.table_seat, assigned=True)
            customer_name = customer.last_name
        except Customer.DoesNotExist:
            customer_name = ''
        try:
            customer = Customer.objects.get(store_id=rchop(obj.table_id, "." + obj.table_seat), table_id=obj.table_seat, seated=True, is_in_store=True)
            customer_name = customer.last_name
        except Customer.DoesNotExist:
            customer_name = ''
        return customer_name

    def get_seated(self, obj):
        try:
            customer = Customer.objects.get(store_id=rchop(obj.table_id, "." + obj.table_seat), table_id='wait_list',
                                            assigned_table_id=obj.table_seat, assigned=True)
            customer_name = customer.seated
        except Customer.DoesNotExist:
            customer_name = False
        try:
            customer = Customer.objects.get(store_id=rchop(obj.table_id, "." + obj.table_seat), table_id=obj.table_seat, seated=True, is_in_store=True)
            customer_name = customer.seated
        except Customer.DoesNotExist:
            customer_name = False
        return customer_name

    def get_phone(self, obj):
        try:
            customer = Customer.objects.get(store_id=rchop(obj.table_id, "." + obj.table_seat), table_id='wait_list',
                                            assigned_table_id=obj.table_seat, assigned=True)
            return customer.phone
        except Customer.DoesNotExist:
            return ''

    def get_record_number(self, obj):
        try:
            customer = Customer.objects.get(store_id=rchop(obj.table_id, "." + obj.table_seat), table_id='wait_list',
                                            assigned_table_id=obj.table_seat, assigned=True)
            return customer.record_number
        except Customer.DoesNotExist:
            return ''


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class ServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceItem
        fields = '__all__'
