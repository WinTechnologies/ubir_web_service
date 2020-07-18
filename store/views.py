from datetime import datetime, timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist

from customer.models import Customer
from order.models import Order
from .models import Store, StoreServiceItem
from .serializers import StoreSerializer, ServiceItemSerializer, StoreServiceItemSerializer
from users.permissions import IsOnTable


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    http_method_names = ['post']

    @action(detail=False, methods=['post'], permission_classes=[IsOnTable], url_path='get_store_information')
    def get_store_information(self, request):
        phone_number = request.data['phone_number']
        company_id = request.data['companyId']
        store_id = request.data['storeId']
        table_id = request.data['tableId']
        response_data = {}
        try:
            customer = Customer.objects.get(phone=phone_number)
            customer.company_id = company_id
            customer.store_id = store_id
            customer.table_id = table_id
            customer.save()
            store_id = customer.store_id
            store = Store.objects.get(store_id=store_id)
            order_items = []
            for store_service_item in StoreServiceItem.objects.filter(store__store_id=store_id):
                for service_item in store_service_item.service_item.all():
                    data = ServiceItemSerializer(instance=service_item).data
                    try:
                        order = Order.objects.get(customer=customer, store=store, service_item=service_item, table_id=table_id)
                        data['quantity'] = order.quantity
                        data['status'] = order.status
                        data['timer'] = int((datetime.now(timezone.utc) - order.start_time).total_seconds())
                    except:
                        data['quantity'] = 0
                        data['timer'] = 0
                        data['status'] = Order.PENDING
                    order_items.append(data)
            response_data['order_items'] = order_items
            response_data['store_logo'] = store.logo.url
            response_data['store_id'] = store.store_id
            response_data['store_location'] = store.name
            response_data['order_url'] = store.order_url
            response_data['timer_turn_yellow'] = store.timer_turn_yellow
            response_data['timer_turn_red'] = store.timer_turn_red
            response_data['timer_escalation_to_manager'] = store.timer_escalation_to_manager
            response_data['table_id'] = customer.table_id
            return Response(response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Please verify your phone number."})
