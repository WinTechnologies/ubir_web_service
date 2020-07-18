# chat/consumers.py
import json
from datetime import datetime, timezone
from rest_framework.authtoken.models import Token
from channels.generic.websocket import AsyncWebsocketConsumer

from service.models import Serviceman
from order.models import Order
from chat.models import Message
from customer.models import Customer
from store.models import Store, ServiceItem, StoreServiceItem
from chat.serializers import MessageSerializer
from order.serializers import OrderSerializer


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
            customer = Customer.objects.get(phone=phone_number)
            store = Store.objects.get(store_id=store_id)
            service_item = ServiceItem.objects.get(pk=service_item_id)
            order, created = Order.objects.get_or_create(customer=customer, store=store, service_item=service_item)
            order.quantity = order.quantity + 1
            order.table_id = table_id
            order.start_time = datetime.now(timezone.utc)
            order.status = Order.PENDING
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
            order = Order.objects.get(record_number=record_number)
            order.status = Order.INPROGRESS
            order.save()
            data = OrderSerializer(instance=order).data
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_service_request',
                    'message': data
                }
            )
        elif data['command'] == 'complete_order_item':
            record_number = data['record_number']
            order = Order.objects.get(record_number=record_number)
            order.status = Order.COMPLETED
            order.quantity = 0
            order.save()
            data = OrderSerializer(instance=order).data
            table_id = order.table_id
            store_id = order.store.store_id
            item_title = order.service_item.title
            Message.objects.filter(table_id=table_id, store_id=store_id, item_title=item_title).delete()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'complete_order_item',
                    'message': data
                }
            )
        elif data['command'] == 'new_message_to_table':
            store_id = data['store_id']
            table_seat = data['table_seat']
            item_title = data['item_title']
            message_text = data['message']
            message, created = Message.objects.get_or_create(table_id=table_seat,
                                                             store_id=store_id,
                                                             item_title=item_title,
                                                             type=Message.QUESTION,
                                                             message=message_text,
                                                             is_seen=False)
            message.save()
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
            message, created = Message.objects.get_or_create(table_id=table_seat,
                                                             store_id=store_id,
                                                             item_title=item_title,
                                                             type=Message.ANSWER,
                                                             message=message_text,
                                                             is_seen=False)
            message.save()
            data = MessageSerializer(instance=message).data
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
            response_data = []
            for store_service_item in StoreServiceItem.objects.filter(store__store_id=store_id):
                for service_item in store_service_item.service_item.all():
                    item = {}
                    item['item_title'] = service_item.title
                    item['question'] = ''
                    item['answer'] = ''
                    question = Message.objects.filter(store_id=store_id, table_id=table_id, item_title=service_item.title, type=Message.QUESTION).order_by('-created_at').first()
                    if question:
                        item['question'] = question.message
                    answer = Message.objects.filter(store_id=store_id, table_id=table_id, item_title=service_item.title, type=Message.ANSWER).order_by('-created_at').first()
                    if answer:
                        item['answer'] = answer.message
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
            table_ids = data['table_ids']
            response_data = []
            for table_id in data['table_ids']:
                for store_service_item in StoreServiceItem.objects.filter(store__store_id=store_id):
                    for service_item in store_service_item.service_item.all():
                        item = {}
                        item['table_id'] = table_id
                        item['item_title'] = service_item.title
                        item['question'] = ''
                        item['answer'] = ''
                        question = Message.objects.filter(store_id=store_id, table_id=table_id,
                                                          item_title=service_item.title,
                                                          type=Message.QUESTION).order_by('-created_at').first()
                        if question:
                            item['question'] = question.message
                        answer = Message.objects.filter(store_id=store_id, table_id=table_id,
                                                        item_title=service_item.title, type=Message.ANSWER).order_by(
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
