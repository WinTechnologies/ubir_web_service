import os
from twilio.rest import Client
from django.template.loader import render_to_string


class SMSTextSender():

    def __init__(self):
        self.account_sid = os.getenv('SID')
        self.auth_token = os.getenv('SECRET')
        self.from_phone = os.getenv('FROM')
        self.client = Client(self.account_sid, self.auth_token)

    def send_message(self, store_id, table_id, message, api_frontend_url, to_phone):
        template = "sms_message_template.html"
        context = {
            "table_id": table_id,
            "store_id": store_id,
            "message": message,
            "url": api_frontend_url + "/order",
        }
        message = render_to_string(template, context)
        message = message.encode('utf-8')
        message = self.client.messages.create(to=to_phone, from_=self.from_phone, body=message)
        print(message.sid)
