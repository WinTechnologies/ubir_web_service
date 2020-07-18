from django.contrib import admin
from .models import Serviceman


@admin.register(Serviceman)
class ServiceAdmin(admin.ModelAdmin):
    pass
