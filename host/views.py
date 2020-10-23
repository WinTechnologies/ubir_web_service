from datetime import datetime, timezone, timedelta
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from phone_verify.base import response
from rest_framework.authtoken.models import Token

from users.permissions import IsServiceman
from customer.models import Customer
from store.models import Store, TableSeat, DiningType
from service.models import Serviceman
from chat.models import Message
from .utils import SMSTextSender
from customer.serializers import CustomerSerializer
from store.serializers import TableSeatSerializer, StoreSerializer


class HostViewSet(ModelViewSet):
    http_method_names = ['post']

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='get_status_location')
    def get_status_location(self, request):
        response_data = []
        store_id = request.data['store_id']
        store = Store.objects.get(store_id=store_id)
        for table_status in TableSeat.ACTION_STATUS_CHOICES_DICT:
            data = {}
            data['status'] = table_status
            data['inside'] = 0
            for table_seat in store.table_seat.all():
                if table_seat.action_status == table_status and table_seat.location.title.lower() == 'inside':
                    data['inside'] += 1
            data['outside'] = 0
            for table_seat in store.table_seat.all():
                if table_seat.action_status == table_status and table_seat.location.title.lower() == 'outside':
                    data['outside'] += 1
            data['bar'] = 0
            for table_seat in store.table_seat.all():
                if table_seat.action_status == table_status and table_seat.location.title.lower() == 'bar':
                    data['bar'] += 1
            response_data.append(data)
        data = {}
        data['status'] = TableSeat.CLOSED
        data['inside'] = 0
        for table_seat in store.table_seat.all():
            if table_seat.status == TableSeat.CLOSED and table_seat.location.title.lower() == 'inside':
                data['inside'] += 1
        data['outside'] = 0
        for table_seat in store.table_seat.all():
            if table_seat.status == TableSeat.CLOSED and table_seat.location.title.lower() == 'outside':
                data['outside'] += 1
        data['bar'] = 0
        for table_seat in store.table_seat.all():
            if table_seat.status == TableSeat.CLOSED and table_seat.location.title.lower() == 'bar':
                data['bar'] += 1
        response_data.append(data)
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='get_location_wait')
    def get_location_wait(self, request):
        response_data = []
        store_id = request.data['store_id']
        store = Store.objects.get(store_id=store_id)
        wait_time_frame = store.wait_time_frame
        locations = ['Inside', 'Outside', 'Bar', 'First Available']
        for location in locations:
            data = {}
            data['location'] = location
            customers = Customer.objects.filter(store_id=store_id,
                                                table_id='wait_list',
                                                is_in_store=True,
                                                dining_type__title__iexact=location)
            data['waiting'] = len(customers)
            customers = Customer.objects.filter(store_id=store_id,
                                                table_id='wait_list',
                                                is_in_store=True,
                                                dining_type__title__iexact=location,
                                                start_time__gte=datetime.now() - timedelta(
                                                    minutes=wait_time_frame))
            if len(customers) == 0:
                customer = Customer.objects.filter(store_id=store_id,
                                                   table_id='wait_list',
                                                   is_in_store=True,
                                                   dining_type__title__iexact=location).order_by('-start_time').first()
                if customer:
                    data['longest'] = int((datetime.now() - customer.start_time).total_seconds())
                    data['average'] = int((datetime.now() - customer.start_time).total_seconds())
                else:
                    data['longest'] = 0
                    data['average'] = 0
            else:
                sum = 0
                longest = 0
                for customer in customers:
                    sum += (datetime.now() - customer.start_time).total_seconds()
                    if longest < (datetime.now() - customer.start_time).total_seconds():
                        longest = (datetime.now() - customer.start_time).total_seconds()
                data['longest'] = int(longest)
                data['average'] = int(sum / len(customers))
            response_data.append(data)
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='get_wait_list')
    def get_wait_list(self, request):
        token = request.data['token']
        store_id = request.data['store_id']
        token = Token.objects.get(key=token)
        serviceman = Serviceman.objects.get(user=token.user)
        dining_types = []
        for dining_type in DiningType.objects.all():
            if dining_type.action_type == 'Pickup @ Bar':
                if serviceman.togo:
                    dining_types.append(dining_type.title)
            elif dining_type.action_type == 'Delivering to Car/Curbside':
                if serviceman.curbside:
                    dining_types.append(dining_type.title)
            else:
                if serviceman.host:
                    dining_types.append(dining_type.title)
        customers = Customer.objects.filter(store_id=store_id, table_id='wait_list', is_in_store=True, seated=False, dining_type__title__in=dining_types)
        response_data = []
        for customer in customers:
            data = {}
            data['record_number'] = customer.record_number
            data['last_name'] = customer.last_name
            data['first_name'] = customer.first_name
            data['phone_number'] = customer.phone
            data['party_size'] = customer.number_in_party
            data['dining_option'] = customer.dining_type.title
            data['parking_space'] = customer.parking_space
            data['action'] = customer.dining_type.action_type
            data['timer'] = int((datetime.now() - customer.start_time).total_seconds())
            data['assigned'] = customer.assigned
            answer = Message.objects.filter(store_id=store_id, table_id=customer.table_id, phone=customer.phone,
                                            item_title='', type=Message.ANSWER, is_seen=False).order_by('-created_at').first()
            if answer:
                data['answer'] = answer.message
            else:
                data['answer'] = ''
            if not customer.phone:
                data['answer'] = 'Please tell the customer verbally'
            question = Message.objects.filter(store_id=store_id, table_id=customer.table_id, phone=customer.phone,
                                              item_title='', type=Message.QUESTION, is_seen=False).order_by('-created_at').first()
            if question:
                data['question'] = question.message
            else:
                data['question'] = ''
            response_data.append(data)
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='get_store_table_config')
    def get_store_table_config(self, request):
        response_data = []
        store_id = request.data['store_id']
        store = Store.objects.get(store_id=store_id)
        for table_seat in store.table_seat.all():
            data = TableSeatSerializer(instance=table_seat).data
            response_data.append(data)
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='get_store_configuration')
    def get_store_configuration(self, request):
        token = request.data['token']
        store_id = request.data['store_id']
        token = Token.objects.get(key=token)
        serviceman = Serviceman.objects.get(user=token.user)
        store = Store.objects.get(store_id=store_id)
        data = {}
        data["store_config"] = StoreSerializer(instance=store).data
        data["host"] = serviceman.host
        data["togo"] = serviceman.togo
        data["curbside"] = serviceman.curbside
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='send_sms_text')
    def send_sms_text(self, request):
        phone_number = request.data['phone_number']
        message = request.data['message']
        store_id = request.data['store_id']
        store = Store.objects.get(store_id=store_id)
        api_frontend_url = request.data['api_frontend_url']
        sms_text_sender = SMSTextSender()
        try:
            sms_text_sender.send_message(store.name, message, api_frontend_url, phone_number)
            return response.Ok({"message": "Success"})
        except:
            return response.Ok({"message": "Failed"})

    @action(detail=False, methods=['post'], permission_classes=[IsServiceman], url_path='select_dining_option')
    def select_dining_option(self, request):
        token = request.data['token']
        type = request.data['type']
        token = Token.objects.get(key=token)
        serviceman = Serviceman.objects.get(user=token.user)
        if type == 'host':
            serviceman.host = not serviceman.host
        elif type == 'togo':
            serviceman.togo = not serviceman.togo
        elif type == 'curbside':
            serviceman.curbside = not serviceman.curbside
        serviceman.save()
        data = {
            "host": serviceman.host,
            "togo": serviceman.togo,
            "curbside": serviceman.curbside
        }
        return Response(data, status=status.HTTP_200_OK)
