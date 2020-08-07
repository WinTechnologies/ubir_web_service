from django.contrib import admin
from .models import CustomerLog, ServiceLog


class CustomerLogAdmin(admin.ModelAdmin):
    pass


class ServiceLogAdmin(admin.ModelAdmin):
    pass


admin.site.register(CustomerLog, CustomerLogAdmin)
admin.site.register(ServiceLog, ServiceLogAdmin)