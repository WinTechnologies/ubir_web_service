# chat/consumers.py
import json
import random
import string

from datetime import datetime, timezone
from django.db.models import Q
from rest_framework.authtoken.models import Token
from channels.generic.websocket import AsyncWebsocketConsumer

from service.models import Serviceman, ServicemanConfig
from order.models import Order
from chat.models import Message
from customer.models import Customer
from log.models import CustomerLog, ServiceLog
from store.models import Store, ServiceItem, TableSeat
from chat.serializers import MessageSerializer
from order.serializers import OrderSerializer


def convert(seconds):
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['command'] == 'update_order_item':
            store_id = data['store_id']
            table_id = data['table_id']
            service_item_id = data['service_item_id']
            phone_number = data['phone_number']
            session_token = data['session_token']
            customer = Customer.objects.get(phone=phone_number, is_in_store=True)
            store = Store.objects.get(store_id=store_id)
            service_item = ServiceItem.objects.get(pk=service_item_id)
            order = None
            created = False
            try:
                order = Order.objects.get(Q(customer=customer) & Q(store=store) & Q(service_item=service_item) & (Q(status=Order.INPROGRESS)|Q(status=Order.INPROGRESS_PENDING)))
                order.status = Order.INPROGRESS_PENDING
            except:
                pass
            if not order:
                order, created = Order.objects.get_or_create(customer=customer, store=store, service_item=service_item, status=Order.PENDING, session_token=customer.session_token)
            customer_log = CustomerLog(company=store.company.name, store=store.name, login=phone_number,
                                       tap="Item", content=f"{table_id}|{order.record_number}|{order.service_item.title}",
                                       session_token=customer.session_token)
            customer_log.save()
            order.quantity = order.quantity + 1
            order.table_id = table_id
            if created:
                order.start_time = datetime.now()
            else:
                if order.status == Order.COMPLETED:
                    order.start_time = datetime.now()
            order.save()
            # Save the last time the customer taps the item
            table_seat = TableSeat.objects.get(table_id=store_id + "." + table_id, table_seat=table_id)
            table_seat.last_time_customer_tap = datetime.now()
            table_seat.save()
            data = OrderSerializer(instance=order).data
            data['timer'] = int((datetime.now() - order.start_time).total_seconds())
            data['last'] = int((datetime.now() - table_seat.last_time_customer_tap).total_seconds())
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_order_item',
                    'message': data
                }
            )
        elif data['command'] == 'update_service_request':
            record_number = data['record_number']
            token = data['token']
            store_id = data['store_id']
            table_seat = data['table_seat']
            phone_number = data['phone_number']
            store = Store.objects.get(store_id=store_id)
            token = Token.objects.get(key=token)
            serviceman = Serviceman.objects.get(user=token.user)
            order = Order.objects.get(record_number=record_number)
            order.status = Order.INPROGRESS
            order.save()
            data = OrderSerializer(instance=order).data
            data['timer'] = int((datetime.now() - order.start_time).total_seconds())
            data['phone_number'] = phone_number
            # The Serviceman taps 'Clean & Disinfect Table' item
            if order.service_item.title == 'Clean & Disinfect Table':
                table_seat = TableSeat.objects.get(table_seat=table_seat,
                                                   table_id=store.store_id + '.' + table_seat)
                table_seat.action_status = TableSeat.CLEANING
                table_seat.last_time_status_changed = datetime.now()
                table_seat.save()
                data['table_status'] = TableSeat.CLEANING
                service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                         tap="Item",
                                         content=f"{table_seat}|{order.quantity}|{convert(data['timer'])}|{order.service_item.title}",
                                         session_token=token)
                service_log.save()
            elif order.service_item.title == store.pickup_message:
                service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                         tap="Item",
                                         content=f"{table_seat}|{order.quantity}|{convert(data['timer'])}|{order.service_item.title}",
                                         session_token=token)
                service_log.save()
            elif order.service_item.title == store.curside_message:
                service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                         tap="Item",
                                         content=f"{table_seat}|{order.quantity}|{convert(data['timer'])}|{order.service_item.title}",
                                         session_token=token)
                service_log.save()
            else:
                service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                         tap="Item",
                                         content=f"{table_seat}|{order.quantity}|{convert(data['timer'])}|{order.service_item.title}",
                                         session_token=order.customer.session_token)
                service_log.save()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_service_request',
                    'message': data
                }
            )
        elif data['command'] == 'complete_order_item':
            record_number = data['record_number']
            token = data['token']
            store_id = data['store_id']
            table_seat = data['table_seat']
            phone_number = data['phone_number']
            order = Order.objects.get(record_number=record_number)
            quantity = order.quantity
            order.status = Order.COMPLETED
            order.quantity = 0
            order.save()
            data = OrderSerializer(instance=order).data
            data['phone_number'] = phone_number
            item_title = order.service_item.title
            store = Store.objects.get(store_id=store_id)
            token = Token.objects.get(key=token)
            serviceman = Serviceman.objects.get(user=token.user)
            timer = int((datetime.now() - order.start_time).total_seconds())
            if order.service_item.title == 'Clean & Disinfect Table':
                table_seat = TableSeat.objects.get(table_seat=table_seat,
                                                   table_id=store.store_id + '.' + table_seat)
                customers = Customer.objects.filter(store_id=store.store_id, table_id=table_seat.table_seat, is_in_store=True)
                if len(customers) > 0:
                    table_seat.action_status = TableSeat.OCCUPIED
                else:
                    table_seat.action_status = TableSeat.AVAILABLE
                table_seat.last_time_status_changed = datetime.now()
                table_seat.save()
                data['table_status'] = table_seat.action_status
                service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                         tap="Timer",
                                         content=f"{table_seat}|{quantity}|{convert(timer)}|{order.service_item.title}",
                                         session_token=token)
                service_log.save()
            elif order.service_item.title == store.pickup_message:
                service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                         tap="Timer",
                                         content=f"{table_seat}|{quantity}|{convert(timer)}|{order.service_item.title}",
                                         session_token=token)
                service_log.save()
                customer = Customer.objects.get(phone=phone_number)
                customer.is_in_store = False
                customer.save()
            elif order.service_item.title == store.curside_message:
                service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                         tap="Timer",
                                         content=f"{table_seat}|{quantity}|{convert(timer)}|{order.service_item.title}",
                                         session_token=token)
                service_log.save()
                customer = Customer.objects.get(phone=phone_number)
                customer.is_in_store = False
                customer.save()
            else:
                service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                         tap="Timer", content=f"{table_seat}|{quantity}|{convert(timer)}|{order.service_item.title}",
                                         session_token=order.customer.session_token)
                service_log.save()
                messages = Message.objects.filter(table_id=table_seat, store_id=store_id, item_title=item_title,
                                                  phone=order.customer.phone)
                for message in messages:
                    message.is_seen = True
                    message.save()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'complete_order_item',
                    'message': data
                }
            )
        elif data['command'] == 'new_message_to_table':
            record_number = data['record_number']
            store_id = data['store_id']
            table_seat = data['table_seat']
            item_title = data['item_title']
            message_text = data['message']
            token = data['token']
            store = Store.objects.get(store_id=store_id)
            token = Token.objects.get(key=token)
            serviceman = Serviceman.objects.get(user=token.user)
            order = Order.objects.get(record_number=record_number)
            timer = int((datetime.now() - order.start_time).total_seconds())
            message, created = Message.objects.get_or_create(table_id=table_seat,
                                                             store_id=store_id,
                                                             item_title=item_title,
                                                             type=Message.QUESTION,
                                                             message=message_text,
                                                             phone=order.customer.phone,
                                                             session_token=order.customer.session_token,
                                                             is_seen=False)
            message.save()
            service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                     tap="Message", content=f"{table_seat}|{order.quantity}|{convert(timer)}|{message_text}|{item_title}",
                                     session_token=order.customer.session_token)
            service_log.save()
            data = MessageSerializer(instance=message).data
            data['order_number'] = record_number
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_message_to_table',
                    'message': data
                }
            )
        elif data['command'] == 'new_message_to_service':
            store_id = data['store_id']
            table_seat = data['table_seat']
            item_title = data['item_title']
            message_text = data['message']
            phone_number = data['phone_number']
            session_token = data['session_token']
            customer = Customer.objects.get(phone=phone_number, is_in_store=True)
            store = Store.objects.get(store_id=store_id)
            message, created = Message.objects.get_or_create(table_id=table_seat,
                                                             store_id=store_id,
                                                             item_title=item_title,
                                                             type=Message.ANSWER,
                                                             message=message_text,
                                                             phone=phone_number,
                                                             session_token=customer.session_token,
                                                             is_seen=False)
            message.save()
            data = MessageSerializer(instance=message).data
            order = Order.objects.get(Q(customer=customer) & Q(store=store) & Q(service_item__title=item_title) & Q(table_id=table_seat) & ~Q(status=Order.COMPLETED))
            timer = int((datetime.now() - order.start_time).total_seconds())
            customer_log = CustomerLog(company=store.company.name, store=store.name, login=phone_number,
                                       tap="Message", content=f"{table_seat}|{order.record_number}|{order.service_item.title}|{order.quantity}|{convert(timer)}|{message_text}",
                                       session_token=session_token)
            customer_log.save()
            data['order_number'] = order.record_number
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_message_to_service',
                    'message': data
                }
            )
        elif data['command'] == 'fetch_table_messages':
            store_id = data['store_id']
            table_id = data['table_id']
            phone_number = data['phone_number']
            store = Store.objects.get(store_id=store_id)
            response_data = []
            for service_item in store.service_item.all():
                item = {}
                item['item_title'] = service_item.title
                item['question'] = ''
                item['answer'] = ''
                question = Message.objects.filter(store_id=store_id, table_id=table_id, phone=phone_number, item_title=service_item.title, type=Message.QUESTION, is_seen=False).order_by('-created_at').first()
                if question:
                    item['question'] = question.message
                answer = Message.objects.filter(store_id=store_id, table_id=table_id, phone=phone_number, item_title=service_item.title, type=Message.ANSWER, is_seen=False).order_by('-created_at').first()
                if answer:
                    item['answer'] = answer.message
                item['table_id'] = table_id
                item['store_id'] = store_id
                item['phone_number'] = phone_number
                response_data.append(item)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'fetch_table_messages',
                    'message': response_data
                }
            )
        elif data['command'] == 'fetch_messages':
            store_id = data['store_id']
            token = data['token']
            table_ids = []
            store = Store.objects.get(store_id=store_id)
            token = Token.objects.get(key=token)
            serviceman = Serviceman.objects.get(user=token.user)
            serviceman_configs = ServicemanConfig.objects.filter(serviceman=serviceman)
            for serviceman_config in serviceman_configs:
                table_ids.append(serviceman_config.table_seat)
            response_data = []
            for table_id in table_ids:
                for service_item in store.service_item.all():
                    for customer in Customer.objects.filter(store_id=store_id, table_id=table_id, is_in_store=True):
                        item = {}
                        item['table_id'] = table_id
                        item['item_title'] = service_item.title
                        item['question'] = ''
                        item['answer'] = ''
                        question = Message.objects.filter(store_id=store_id, table_id=table_id,
                                                          item_title=service_item.title,
                                                          type=Message.QUESTION,
                                                          phone=customer.phone,
                                                          is_seen=False).order_by('-created_at').first()
                        if question:
                            item['question'] = question.message
                        answer = Message.objects.filter(store_id=store_id, table_id=table_id,
                                                        item_title=service_item.title, type=Message.ANSWER, phone=customer.phone, is_seen=False).order_by(
                            '-created_at').first()
                        if answer:
                            item['answer'] = answer.message
                        try:
                            order = Order.objects.filter(customer=customer, store=store, table_id=table_id, service_item=service_item).exclude(status=Order.COMPLETED).first()
                            record_number = order.record_number
                        except:
                            record_number = ''
                        item['record_number'] = record_number
                        response_data.append(item)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'fetch_messages',
                    'message': response_data
                }
            )
        elif data['command'] == 'open_close_table':
            token = data['token']
            table_seat = data['table_seat']
            token = Token.objects.get(key=token)
            serviceman = Serviceman.objects.get(user=token.user)
            try:
                table_seat = TableSeat.objects.get(table_seat=table_seat, table_id=serviceman.store.store_id + '.' + table_seat)
                if table_seat.status == TableSeat.OPEN:
                    table_seat.status = TableSeat.CLOSED
                else:
                    table_seat.status = TableSeat.OPEN
                table_seat.save()
                response_data = {"status": table_seat.status, "table_seat": table_seat.table_seat}
            except:
                response_data = {}
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'open_close_table',
                    'message': response_data
                }
            )
        elif data['command'] == 'reset_table':
            token = data['token']
            table_seat = data['table_seat']
            store_id = data['store_id']
            token = Token.objects.get(key=token)
            serviceman = Serviceman.objects.get(user=token.user)
            try:
                response_data = {}
                try:
                    customers = Customer.objects.filter(is_in_store=True, store_id=store_id, table_id=table_seat)
                    for customer in customers:
                        customer.is_in_store = False
                        customer.save()
                except:
                    pass
                orders = Order.objects.filter(store__store_id=store_id, table_id=table_seat)
                phone_numbers = []
                for order in orders:
                    order.status = Order.COMPLETED
                    order.save()
                messages = Message.objects.filter(store_id=store_id, table_id=table_seat, is_seen=False)
                for message in messages:
                    message.is_seen = True
                    message.save()
                table_seat = TableSeat.objects.get(table_seat=table_seat, table_id=store_id + '.' + table_seat)
                table_seat.seated_time = None
                table_seat.ordered_time = None
                table_seat.save()
                response_data = {"message": "success", "store_id": store_id, "table_id": table_seat.table_seat}
            except:
                response_data = {}
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'reset_table',
                    'message': response_data
                }
            )
        elif data['command'] == 'assign_table':
            token = data['token']
            table_seat = data['table_seat']
            store_id = data['store_id']
            phone_number = data["phone_number"]
            config_or_wait = data["config_or_wait"]
            response_data = {}
            try:
                customer = Customer.objects.get(phone=phone_number)
            except:
                customer = Customer(phone=phone_number)
            customer.store_id = store_id
            customer.table_id = table_seat
            customer.is_in_store = True
            session_token = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(25))
            customer.session_token = session_token
            customer.save()
            table_seat = TableSeat.objects.get(table_seat=table_seat, table_id=store_id + '.' + table_seat)
            table_seat.action_status = TableSeat.OCCUPIED
            table_seat.last_time_status_changed = datetime.now()
            table_seat.seated_time = datetime.now()
            table_seat.save()
            # table_seat
            response_data = {"is_authenticated": True,
                             "config_or_wait": config_or_wait,
                             "session_token": session_token,
                             "phone_number": phone_number,
                             "table_seat": table_seat.table_seat,
                             "store_id": store_id,
                             "table_status": table_seat.action_status,
                             "seated_time": table_seat.seated_time.strftime("%H:%M %p")}
            await self.channel_layer.group_send(self.room_group_name,
                                                {'type': 'assign_table', 'message': response_data})
        elif data['command'] == 'clean_table':
            token = data['token']
            store_id = data['store_id']
            table_seat = data['table_seat']
            service_item_title = data['service_item_title']
            response_data = {}
            store = Store.objects.get(store_id=store_id)
            service_item, created = ServiceItem.objects.get_or_create(title=service_item_title)
            try:
                order = Order.objects.get(Q(store=store) & Q(table_id=table_seat) & Q(service_item=service_item) & (
                            Q(status=Order.INPROGRESS) | Q(status=Order.INPROGRESS_PENDING)))
                order.status = Order.INPROGRESS_PENDING
            except:
                order = None
                pass
            if not order:
                order, created = Order.objects.get_or_create(table_id=table_seat, store=store, service_item=service_item,
                                                             status=Order.PENDING, session_token=token)
            order.quantity = 1
            order.table_id = table_seat
            if created:
                order.start_time = datetime.now()
            else:
                if order.status == Order.COMPLETED:
                    order.start_time = datetime.now()
            order.save()
            data = OrderSerializer(instance=order).data
            data['timer'] = int((datetime.now() - order.start_time).total_seconds())
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'clean_table',
                    'message': data
                }
            )
        elif data['command'] == 'new_message_to_wait_list':
            phone_number = data['phone_number']
            message_text = data['message']
            store_id = data['store_id']
            token = data['token']
            customer = Customer.objects.get(phone=phone_number)
            message, created = Message.objects.get_or_create(table_id=customer.table_id,
                                                             store_id=store_id,
                                                             item_title='',
                                                             type=Message.QUESTION,
                                                             message=message_text,
                                                             phone=phone_number,
                                                             session_token=customer.session_token,
                                                             is_seen=False)
            message.save()
            data = MessageSerializer(instance=message).data
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_message_to_wait_list',
                    'message': data
                }
            )
        elif data['command'] == 'new_message_to_host':
            phone_number = data['phone_number']
            message_text = data['message']
            store_id = data['store_id']
            table_seat = data['table_seat']
            session_token = data['session_token']
            customer = Customer.objects.get(phone=phone_number)
            message, created = Message.objects.get_or_create(table_id=table_seat,
                                                             store_id=store_id,
                                                             item_title='',
                                                             type=Message.ANSWER,
                                                             message=message_text,
                                                             phone=phone_number,
                                                             session_token=session_token,
                                                             is_seen=False)
            message.save()
            data = MessageSerializer(instance=message).data
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'new_message_to_host',
                    'message': data
                }
            )
        elif data['command'] == 'add_parking_space':
            phone_number = data['phone_number']
            parking_space = data['parking_space']
            customer = Customer.objects.get(phone=phone_number)
            customer.parking_space = parking_space
            customer.save()
            data = {"phone_number": phone_number, "parking_space": parking_space}
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'add_parking_space',
                    'message': data
                }
            )
        elif data['command'] == 'deliver_to_car':
            phone_number = data['phone_number']
            store_id = data['store_id']
            token = data['token']
            service_item_title = data['message']
            table_seat = 'Wait'
            store = Store.objects.get(store_id=store_id)
            customer = Customer.objects.get(phone=phone_number)
            service_item, created = ServiceItem.objects.get_or_create(title=service_item_title)
            try:
                order = Order.objects.get(Q(store=store) & Q(table_id=table_seat) & Q(service_item=service_item) & (
                        Q(status=Order.INPROGRESS) | Q(status=Order.INPROGRESS_PENDING)))
                order.status = Order.INPROGRESS_PENDING
            except:
                order = None
                pass
            if not order:
                order, created = Order.objects.get_or_create(table_id=table_seat, store=store,
                                                             service_item=service_item,
                                                             status=Order.PENDING, session_token=token)
            order.quantity = 1
            order.table_id = table_seat
            order.customer = customer
            if created:
                order.start_time = datetime.now()
            else:
                if order.status == Order.COMPLETED:
                    order.start_time = datetime.now()
            order.save()
            data = OrderSerializer(instance=order).data
            data['timer'] = int((datetime.now() - order.start_time).total_seconds())
            data['phone_number'] = phone_number
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'deliver_to_car',
                    'message': data
                }
            )
        elif data['command'] == 'pickup_bar':
            phone_number = data['phone_number']
            store_id = data['store_id']
            token = data['token']
            service_item_title = data['message']
            table_seat = 'Wait'
            store = Store.objects.get(store_id=store_id)
            customer = Customer.objects.get(phone=phone_number)
            service_item, created = ServiceItem.objects.get_or_create(title=service_item_title)
            try:
                order = Order.objects.get(Q(store=store) & Q(table_id=table_seat) & Q(service_item=service_item) & (
                        Q(status=Order.INPROGRESS) | Q(status=Order.INPROGRESS_PENDING)))
                order.status = Order.INPROGRESS_PENDING
            except:
                order = None
                pass
            if not order:
                order, created = Order.objects.get_or_create(table_id=table_seat, store=store,
                                                             service_item=service_item,
                                                             status=Order.PENDING, session_token=token)
            order.quantity = 1
            order.table_id = table_seat
            order.customer = customer
            if created:
                order.start_time = datetime.now()
            else:
                if order.status == Order.COMPLETED:
                    order.start_time = datetime.now()
            order.save()
            data = OrderSerializer(instance=order).data
            data['timer'] = int((datetime.now() - order.start_time).total_seconds())
            data['phone_number'] = phone_number
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'pickup_bar',
                    'message': data
                }
            )

    # Receive message from room group
    async def fetch_table_messages(self, data):
        message = data['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_table_messages'
        }))

    # Receive message from room group
    async def fetch_messages(self, data):
        message = data['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_messages'
        }))

    # Receive message from room group
    async def new_message_to_table(self, data):
        message = data['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'message_from_service'
        }))

    # Receive message from room group
    async def new_message_to_service(self, data):
        message = data['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'message_from_table'
        }))

    async def update_service_request(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_service_request'
        }))

    async def update_order_item(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_order_item'
        }))

    async def complete_order_item(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_completed_order_item'
        }))

    async def open_close_table(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_open_close_table'
        }))

    async def reset_table(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_reset_table'
        }))

    async def assign_table(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_assign_table'
        }))

    async def clean_table(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_clean_table'
        }))

    async def new_message_to_wait_list(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'message_from_host_to_wait_list'
        }))

    async def new_message_to_host(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'message_from_wait_list_to_host'
        }))

    async def add_parking_space(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_parking_space'
        }))

    async def deliver_to_car(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_deliver_to_car'
        }))

    async def pickup_bar(self, data):
        message = data['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'command': 'set_pickup_bar'
        }))