from datetime import datetime, timezone
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist

from .models import Serviceman
from order.models import Order
from store.models import ServiceItem, StoreServiceItem, Store
from .serializers import ServicemanSerializer
from order.serializers import OrderSerializer


class ServiceViewSet(ModelViewSet):
    serializer_class = ServicemanSerializer
    queryset = Serviceman.objects.all()

    @action(detail=False, methods=['post'], url_path='get_order_information')
    def get_order_information(self, request):
        try:
            table_ids = request.data['table_ids']
            serviceman = Serviceman.objects.get(user=request.user)
            orders = Order.objects.filter(store=serviceman.store, table_id__in=table_ids).exclude(status=Order.COMPLETED)
            response_data = []
            for order in orders:
                data = OrderSerializer(instance=order).data
                data['timer'] = int((datetime.now(timezone.utc) - order.start_time).total_seconds())
                response_data.append(data)
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Please verify your phone number."})
