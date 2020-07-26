from django import forms
from django.contrib import admin
from .models import ServiceItem, TableSeat, Store, Company


class ServiceItemAdmin(admin.ModelAdmin):
    pass


class TableSeatAdmin(admin.ModelAdmin):
    pass


class ServiceItemMembershipInline(admin.TabularInline):
    model = Store.service_item.through


class TableSeatMembershipInline(admin.TabularInline):
    model = Store.table_seat.through


class StoreAdmin(admin.ModelAdmin):
    inlines = [
        ServiceItemMembershipInline,
        TableSeatMembershipInline
    ]
    exclude = ('service_item', 'table_seat', )


class CompanyAdmin(admin.ModelAdmin):
    pass


admin.site.register(ServiceItem, ServiceItemAdmin)
admin.site.register(TableSeat, TableSeatAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Company, CompanyAdmin)
