from datetime import datetime, timezone
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist

from .models import Serviceman, ServicemanConfig
from order.models import Order
from store.models import ServiceItem, Store, StoreTableStatus
from customer.models import Customer
from chat.models import Message
from .serializers import ServicemanSerializer
from order.serializers import OrderSerializer
from users.permissions import IsServiceman


class ServiceViewSet(ModelViewSet):
    serializer_class = ServicemanSerializer
    queryset = Serviceman.objects.all()

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='get_store_configs')
    def get_store_configs(self, request):
        store_id = request.data['storeId']
        try:
            serviceman = Serviceman.objects.get(user=request.user)
            store = Store.objects.get(store_id=store_id)
            response_data = []
            for table_seat in store.table_seat.all():
                data = {}
                data['table_seat'] = table_seat.table_seat
                try:
                    serviceman_config = ServicemanConfig.objects.get(serviceman=serviceman, table_seat=table_seat.table_seat)
                    data['table_filter'] = True  # Selected
                except:
                    data['table_filter'] = False # Not Selected
                data['reset_table'] = 'Reset'
                store_table_status = StoreTableStatus.objects.get(store=serviceman.store, table_seat=table_seat)
                data['table_status'] = store_table_status.status  # Open
                response_data.append(data)
            return Response(response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Internal Server Error"})

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='reset_table')
    def reset_table(self, request):
        table_seat = request.data['table_seat']
        store_id = request.data['store_id']
        try:
            response_data = []
            customer = Customer.objects.get(is_in_store=True, store_id=store_id, table_id=table_seat)
            customer.is_in_store = True
            customer.save()
            orders = Order.objects.filter(store__store_id=store_id, table_id=table_seat)
            for order in orders:
                order.status = Order.COMPLETED
                order.save()
            messages = Message.objects.filter(store_id=store_id, table_id=table_seat, is_seen=False)
            for message in messages:
                message.is_seen = True
                message.save()
            return Response({"message": "Success"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Internal Server Error"})

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='open_close_table')
    def open_close_table(self, request):
        table_seat = request.data['table_seat']
        serviceman = Serviceman.objects.get(user=request.user)
        try:
            store_table_status = StoreTableStatus.objects.get(store=serviceman.store, table_seat=table_seat)
            if store_table_status.status == StoreTableStatus.OPEN:
                store_table_status.status = StoreTableStatus.CLOSED
            else:
                store_table_status.status = StoreTableStatus.OPEN
            store_table_status.save()
            return Response({"message": store_table_status.status}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Internal Server Error"})

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='select_table')
    def select_table(self, request):
        table_seat = request.data['table_seat']
        selected = request.data['selected']
        try:
            serviceman = Serviceman.objects.get(user=request.user)
            if selected:
                ServicemanConfig.objects.get_or_create(serviceman=serviceman, table_seat=table_seat)
            else:
                ServicemanConfig.objects.filter(serviceman=serviceman, table_seat=table_seat).delete()
            return Response({"message": "Success"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Internal Server Error"})

    @action(detail=False, methods=['post'], url_path='get_order_information')
    def get_order_information(self, request):
        try:
            table_ids = []
            serviceman = Serviceman.objects.get(user=request.user)
            serviceman_configs = ServicemanConfig.objects.filter(serviceman=serviceman)
            for serviceman_config in serviceman_configs:
                table_ids.append(serviceman_config.table_seat)
            orders = Order.objects.filter(store=serviceman.store, table_id__in=table_ids).exclude(status=Order.COMPLETED)
            response_data = []
            for order in orders:
                data = OrderSerializer(instance=order).data
                data['timer'] = int((datetime.now(timezone.utc) - order.start_time).total_seconds())
                response_data.append(data)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Please verify your phone number."})
