from django.contrib import admin
from .models import Customer, UBIRWiFi


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(UBIRWiFi)
class UBIRWiFiAdmin(admin.ModelAdmin):
    pass
