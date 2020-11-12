import os
from twilio.rest import Client
from django.template.loader import render_to_string


class SMSTextSender():

    def __init__(self):
        self.account_sid = os.getenv('SID')
        self.auth_token = os.getenv('SECRET')
        self.from_phone = os.getenv('FROM')
        self.client = Client(self.account_sid, self.auth_token)

    def send_pickup_message(self, to_phone, customer_url):
        template = "pickup_message_template.html"
        context = {
            "customer_url": customer_url
        }
        message = render_to_string(template, context)
        message = message.encode('utf-8')
        message = self.client.messages.create(to=to_phone, from_=self.from_phone, body=message)
        print(message.sid)

    def send_deliver_message(self, to_phone, customer_url, company_name, store_name):
        template = "deliver_message_template.html"
        context = {
            "company_name": company_name,
            "store_name": store_name,
            "customer_url": customer_url
        }
        message = render_to_string(template, context)
        message = message.encode('utf-8')
        message = self.client.messages.create(to=to_phone, from_=self.from_phone, body=message)
        print(message.sid)

    def send_assign_message(self, to_phone, customer_url):
        template = "assign_message_template.html"
        context = {
            "customer_url": customer_url
        }
        message = render_to_string(template, context)
        message = message.encode('utf-8')
        message = self.client.messages.create(to=to_phone, from_=self.from_phone, body=message)
        print(message.sid)

    def send_seat_message(self, to_phone, customer_url):
        template = "seat_message_template.html"
        context = {
            "customer_url": customer_url
        }
        message = render_to_string(template, context)
        message = message.encode('utf-8')
        message = self.client.messages.create(to=to_phone, from_=self.from_phone, body=message)
        print(message.sid)
