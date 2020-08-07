from datetime import datetime, timezone
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token

from .models import ServiceLog, CustomerLog
from service.models import Serviceman
from store.models import Store
from users.permissions import IsServiceman, IsOnTable


class LogViewSet(ModelViewSet):
    http_method_names = ['post']

    @action(detail=False, methods=['post'], url_path='log_tap_table_header_column', permission_classes = [IsServiceman])
    def log_tap_table_header_column(self, request):
        try:
            token = request.data['token']
            store_id = request.data['storeId']
            store = Store.objects.get(store_id=store_id)
            token = Token.objects.get(key=token)
            serviceman = Serviceman.objects.get(user=token.user)
            service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                     tap="Table", content="")
            service_log.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "error"})

    @action(detail=False, methods=['post'], url_path='log_tap_place_new_order', permission_classes=[IsOnTable])
    def log_tap_place_new_order(self, request):
        try:
            store_id = request.data['storeId']
            table_id = request.data['tableId']
            store = Store.objects.get(store_id=store_id)
            phone_number_without_code = request.data['phone_number']
            customer_log = CustomerLog(company=store.company.name, store=store.name, login=phone_number_without_code,
                                       tap="New Order", content=f"{table_id}|Order")
            customer_log.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "error"})
