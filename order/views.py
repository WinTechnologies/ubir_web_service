from datetime import datetime, timezone
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Order
from customer.models import Customer
from store.models import Store, ServiceItem
from .serializers import OrderSerializer
from users.permissions import IsOnTable


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsOnTable]
    http_method_names = ['post']

    @action(detail=False, methods=['post'], url_path='order_item')
    def order_item(self, request):
        try:
            store_id = request.data['store_id']
            table_id = request.data['table_id']
            phone_number = request.data['phone_number']
            quantity = request.data['quantity']
            service_item_id = request.data['service_item_id']
            customer = Customer.objects.get(phone=phone_number)
            store = Store.objects.get(store_id=store_id)
            service_item = ServiceItem.objects.get(pk=service_item_id)
            order, created = Order.objects.get_or_create(customer=customer, store=store, service_item=service_item)
            order.quantity = quantity
            order.table_id = table_id
            order.start_time = datetime.now(timezone.utc)
            order.save()
            data = OrderSerializer(instance=order).data
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "You can not order the item now."})
