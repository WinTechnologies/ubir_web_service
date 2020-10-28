import json

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse_lazy, path, re_path
from django.http import HttpResponseRedirect
from rest_framework.authtoken.models import Token

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from .models import Serviceman
from chat.consumers import ChatConsumer


@admin.register(Serviceman)
class ServiceAdmin(admin.ModelAdmin):
    exclude = ['host', 'togo', 'curbside']

    list_display = (
        'user',
        'account_actions',
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<account_id>/host/logout/', self.admin_site.admin_view(self.host_logout), name='host-logout',),
        ]
        return custom_urls + urls

    def host_logout(self, request, account_id, *args, **kwargs):
        serviceman = Serviceman.objects.get(pk=account_id)
        channel_layer = get_channel_layer()
        room_group_name = 'chat_%s' % serviceman.store.store_id
        token = Token.objects.get(user=serviceman.user).key
        response_data = {
            'token': token
        }
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'logout_host',
                'message': response_data
            }
        )
        url = '/admin/service/serviceman'
        return HttpResponseRedirect(url)

    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Logout</a>',
            reverse_lazy('admin:host-logout', args=[obj.pk]),
        )

    account_actions.short_description = 'Account Actions'
    account_actions.allow_tags = True

