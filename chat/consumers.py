# chat/consumers.py
import json
from datetime import datetime, timezone
from django.db.models import Q
from rest_framework.authtoken.models import Token
from channels.generic.websocket import AsyncWebsocketConsumer

from service.models import Serviceman, ServicemanConfig
from order.models import Order
from chat.models import Message
from customer.models import Customer
from log.models import CustomerLog, ServiceLog
from store.models import Store, ServiceItem, StoreTableStatus
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
                order, created = Order.objects.get_or_create(customer=customer, store=store, service_item=service_item, status=Order.PENDING)
            customer_log = CustomerLog(company=store.company.name, store=store.name, login=phone_number,
                                       tap="Item", content=f"{table_id}|{order.record_number}|{order.service_item.title}")
            customer_log.save()
            order.quantity = order.quantity + 1
            order.table_id = table_id
            if created:
                order.start_time = datetime.now(timezone.utc)
            else:
                if order.status == Order.COMPLETED:
                    order.start_time = datetime.now(timezone.utc)
            # order.status = Order.PENDING
            order.save()
            data = OrderSerializer(instance=order).data
            data['timer'] = int((datetime.now(timezone.utc) - order.start_time).total_seconds())
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
            store = Store.objects.get(store_id=store_id)
            token = Token.objects.get(key=token)
            serviceman = Serviceman.objects.get(user=token.user)
            order = Order.objects.get(record_number=record_number)
            order.status = Order.INPROGRESS
            order.save()
            data = OrderSerializer(instance=order).data
            data['timer'] = int((datetime.now(timezone.utc) - order.start_time).total_seconds())
            service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                     tap="Item", content=f"{table_seat}|{order.quantity}|{convert(data['timer'])}")
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
            order = Order.objects.get(record_number=record_number)
            quantity = order.quantity
            order.status = Order.COMPLETED
            order.quantity = 0
            order.save()
            data = OrderSerializer(instance=order).data
            item_title = order.service_item.title
            messages = Message.objects.filter(table_id=table_seat, store_id=store_id, item_title=item_title)
            for message in messages:
                message.is_seen = True
                message.save()
            store = Store.objects.get(store_id=store_id)
            token = Token.objects.get(key=token)
            serviceman = Serviceman.objects.get(user=token.user)
            timer = int((datetime.now(timezone.utc) - order.start_time).total_seconds())
            service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                     tap="Timer", content=f"{table_seat}|{quantity}|{convert(timer)}")
            service_log.save()
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
            timer = int((datetime.now(timezone.utc) - order.start_time).total_seconds())
            message, created = Message.objects.get_or_create(table_id=table_seat,
                                                             store_id=store_id,
                                                             item_title=item_title,
                                                             type=Message.QUESTION,
                                                             message=message_text,
                                                             is_seen=False)
            message.save()
            service_log = ServiceLog(company=store.company.name, store=store.name, login=serviceman.user.username,
                                     tap="Message", content=f"{table_seat}|{order.quantity}|{convert(timer)}|{message_text}")
            service_log.save()
            data = MessageSerializer(instance=message).data
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
            customer = Customer.objects.get(phone=phone_number, is_in_store=True)
            store = Store.objects.get(store_id=store_id)
            message, created = Message.objects.get_or_create(table_id=table_seat,
                                                             store_id=store_id,
                                                             item_title=item_title,
                                                             type=Message.ANSWER,
                                                             message=message_text,
                                                             is_seen=False)
            message.save()
            data = MessageSerializer(instance=message).data
            order = Order.objects.get(Q(customer=customer) & Q(store=store) & Q(service_item__title=item_title) & Q(table_id=table_seat) & ~Q(status=Order.COMPLETED))
            timer = int((datetime.now(timezone.utc) - order.start_time).total_seconds())
            customer_log = CustomerLog(company=store.company.name, store=store.name, login=phone_number,
                                       tap="Message", content=f"{table_seat}|{order.record_number}|{order.service_item.title}|{order.quantity}|{convert(timer)}|{message_text}")
            customer_log.save()
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
            store = Store.objects.get(store_id=store_id)
            response_data = []
            for service_item in store.service_item.all():
                item = {}
                item['item_title'] = service_item.title
                item['question'] = ''
                item['answer'] = ''
                question = Message.objects.filter(store_id=store_id, table_id=table_id, item_title=service_item.title, type=Message.QUESTION, is_seen=False).order_by('-created_at').first()
                if question:
                    item['question'] = question.message
                answer = Message.objects.filter(store_id=store_id, table_id=table_id, item_title=service_item.title, type=Message.ANSWER, is_seen=False).order_by('-created_at').first()
                if answer:
                    item['answer'] = answer.message
                item['table_id'] = table_id
                item['store_id'] = store_id
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
                    item = {}
                    item['table_id'] = table_id
                    item['item_title'] = service_item.title
                    item['question'] = ''
                    item['answer'] = ''
                    question = Message.objects.filter(store_id=store_id, table_id=table_id,
                                                      item_title=service_item.title,
                                                      type=Message.QUESTION,
                                                      is_seen=False).order_by('-created_at').first()
                    if question:
                        item['question'] = question.message
                    answer = Message.objects.filter(store_id=store_id, table_id=table_id,
                                                    item_title=service_item.title, type=Message.ANSWER, is_seen=False).order_by(
                        '-created_at').first()
                    if answer:
                        item['answer'] = answer.message
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
                store_table_status = StoreTableStatus.objects.get(store=serviceman.store, table_seat=table_seat)
                if store_table_status.status == StoreTableStatus.OPEN:
                    store_table_status.status = StoreTableStatus.CLOSED
                else:
                    store_table_status.status = StoreTableStatus.OPEN
                store_table_status.save()
                response_data = {"status": store_table_status.status, "table_seat": table_seat}
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
                for order in orders:
                    order.status = Order.COMPLETED
                    order.save()
                messages = Message.objects.filter(store_id=store_id, table_id=table_seat, is_seen=False)
                for message in messages:
                    message.is_seen = True
                    message.save()
                response_data = {"message": "success", "store_id": store_id, "table_id": table_seat}
            except:
                response_data = {}
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'reset_table',
                    'message': response_data
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
            'message': MessageSerializer(instance=message).data,
            'command': 'message_from_service'
        }))

    # Receive message from room group
    async def new_message_to_service(self, data):
        message = data['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': MessageSerializer(instance=message).data,
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
