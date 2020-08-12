from datetime import datetime, timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist

from customer.models import Customer
from order.models import Order
from .models import Store, Company
from .serializers import StoreSerializer, ServiceItemSerializer
from users.permissions import IsOnTable, IsUBIRLoggedIn, IsServiceman


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
            customer = Customer.objects.get(phone=phone_number,
                                            is_in_store=True,
                                            company_id=company_id,
                                            store_id=store_id,
                                            table_id=table_id)
            store_id = customer.store_id
            store = Store.objects.get(store_id=store_id)
            order_items = []
            for service_item in store.service_item.all():
                data = ServiceItemSerializer(instance=service_item).data
                try:
                    order = Order.objects.filter(customer=customer, store=store, service_item=service_item, table_id=table_id).exclude(status=Order.COMPLETED).first()
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
            response_data['screen_flash'] = store.screen_flash
            response_data['survey_url'] = store.survey_url
            return Response(response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Please verify your phone number."})

    @action(detail=False, methods=['post'], permission_classes=[IsUBIRLoggedIn], url_path='get_store_logo')
    def get_store_logo(self, request):
        company_id = request.data['companyId']
        store_id = request.data['storeId']
        response_data = {}
        try:
            store = Store.objects.get(store_id=store_id)
            response_data['store_logo'] = store.logo.url
            return Response(response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Please verify your phone number."})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='company_store_table_valid')
    def company_store_table_valid(self, request):
        try:
            company_id = request.data['companyId']
        except KeyError:
            return Response({"error": "The company id does not exist."})
        try:
            store_id = request.data['storeId']
        except KeyError:
            return Response({"error": "The store id does not exist"})
        try:
            table_id = request.data['tableId']
        except KeyError:
            return Response({"error": "The table id does not exist."})
        try:
            company = Company.objects.get(company_id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "The company id is invalid."})
        try:
            store = Store.objects.get(store_id=store_id, company=company)
        except Store.DoesNotExist:
            return Response({"error": "The store id is invalid."})
        if not store.table_seat.filter(table_seat=table_id).exists():
            return Response({"error": "The table id is invalid."})
        return Response({"error": ""}, status=status.HTTP_200_OK)
