import pytz
from datetime import datetime, timedelta
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist

from customer.models import Customer
from order.models import Order
from chat.models import Message
from .models import Store, Company
from .serializers import StoreSerializer, ServiceItemSerializer
from users.permissions import IsOnTable, IsUBIRLoggedIn


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
                    data['timer'] = int((datetime.now(pytz.timezone(store.timezone)) - order.start_time).total_seconds())
                except:
                    data['quantity'] = 0
                    data['timer'] = 0
                    data['status'] = Order.PENDING
                order_items.append(data)
            response_data['order_items'] = order_items
            if store.logo and hasattr(store.logo, 'url'):
                response_data['store_logo'] = store.logo.url
            else:
                response_data['store_logo'] = ''
            response_data['store_id'] = store.store_id
            response_data['store_location'] = store.name
            response_data['order_url'] = store.order_url
            response_data['timer_turn_yellow'] = store.timer_turn_yellow
            response_data['timer_turn_red'] = store.timer_turn_red
            response_data['timer_escalation_to_manager'] = store.timer_escalation_to_manager
            response_data['table_id'] = customer.table_id
            response_data['screen_flash'] = store.screen_flash
            response_data['survey_url'] = store.survey_url
            response_data['order_rank'] = store.order_rank
            response_data['pickup_message'] = store.pickup_message
            response_data['curside_message'] = store.curside_message
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

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='get_dining_types')
    def get_dining_types(self, request):
        company_id = request.data['companyId']
        store_id = request.data['storeId']
        response_data = []
        try:
            store = Store.objects.get(store_id=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store does not exist."}, status=status.HTTP_404_NOT_FOUND)
        for dining_type in store.dining_type.all():
            response_data.append({"title": dining_type.title, "id": dining_type.id})
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsOnTable], url_path='get_company_information')
    def get_company_information(self, request):
        company_id = request.data['companyId']
        try:
            company = Company.objects.get(company_id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company does not exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"company_name": company.name}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsOnTable], url_path='get_customer_information')
    def get_customer_information(self, request):
        phone_number = request.data['phone_number']
        store_id = request.data['storeId']
        table_id = request.data['tableId']
        try:
            customer = Customer.objects.get(phone=phone_number)
        except Customer.DoesNotExist:
            return Response({"error": "Customer does not exists."}, status=status.HTTP_404_NOT_FOUND)
        question = Message.objects.filter(store_id=store_id, table_id=table_id, phone=phone_number,
                                          item_title='', type=Message.QUESTION,
                                          is_seen=False).order_by('-created_at').first()
        answer = Message.objects.filter(store_id=store_id, table_id=table_id, phone=phone_number,
                                        item_title='', type=Message.ANSWER,
                                        is_seen=False).order_by('-created_at').first()
        if question:
            received_message = question.message
        else:
            received_message = ''
        if answer:
            sent_message = answer.message
        else:
            sent_message = ''
        store = Store.objects.get(store_id=store_id)
        location = customer.dining_type.title
        wait_time_frame = store.wait_time_frame
        longest = 0
        average = 0
        customers = Customer.objects.filter(store_id=store_id,
                                            table_id='wait_list',
                                            is_in_store=True,
                                            dining_type__title__iexact=location)
        customers = Customer.objects.filter(store_id=store_id,
                                            table_id='wait_list',
                                            is_in_store=True,
                                            dining_type__title__iexact=location,
                                            start_time__gte=datetime.now(pytz.timezone(store.timezone)) - timedelta(
                                                minutes=wait_time_frame))
        if len(customers) == 0:
            customer = Customer.objects.filter(store_id=store_id,
                                               table_id='wait_list',
                                               is_in_store=True,
                                               dining_type__title__iexact=location).order_by('-start_time').first()
            if customer:
                longest = int((datetime.now(pytz.timezone(store.timezone)) - customer.start_time).total_seconds())
                average = int((datetime.now(pytz.timezone(store.timezone)) - customer.start_time).total_seconds())
            else:
                longest = 0
                average = 0
        else:
            sum = 0
            longest = 0
            for customer in customers:
                sum += (datetime.now(pytz.timezone(store.timezone)) - customer.start_time).total_seconds()
                if longest < (datetime.now(pytz.timezone(store.timezone)) - customer.start_time).total_seconds():
                    longest = (datetime.now(pytz.timezone(store.timezone)) - customer.start_time).total_seconds()
                    longest = int(longest)
            average = int(sum / len(customers))
        customer = Customer.objects.get(phone=phone_number)
        response = {
            "full_name": customer.full_name(),
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "number_in_party": customer.number_in_party,
            "dining_type": customer.dining_type.title,
            "longest_wait": longest,
            "average_wait": average,
            "actual_wait": int((datetime.now(pytz.timezone(store.timezone)) - customer.start_time).total_seconds()),
            "phone_number": phone_number,
            "received_message": received_message,
            "sent_message": sent_message,
            "parking_space": customer.parking_space,
            "waked": customer.waked,
            "assigned_table_id": customer.assigned_table_id
        }
        return Response(response, status=status.HTTP_200_OK)
