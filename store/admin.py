from django import forms
from django.contrib import admin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from .models import ServiceItem, TableSeat, Store, DiningType, Company, StoreTableStatus


class ServiceItemAdmin(admin.ModelAdmin):
    pass


class TableSeatAdmin(admin.ModelAdmin):
    pass


class DiningTypeAdmin(admin.ModelAdmin):
    pass


class ServiceItemMembershipInline(admin.TabularInline):
    model = Store.service_item.through


class TableSeatMembershipInline(admin.TabularInline):
    model = Store.table_seat.through


class DiningTypeMembershipInline(admin.TabularInline):
    model = Store.dining_type.through


class StoreAdmin(admin.ModelAdmin, DynamicArrayMixin):
    inlines = [
        ServiceItemMembershipInline,
        TableSeatMembershipInline,
        DiningTypeMembershipInline
    ]
    exclude = ('service_item', 'table_seat', 'dining_type', )

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.save()
        for key in request.POST:
            if key.startswith('Store_table_seat-') and key.endswith('-tableseat'):
                id = key.replace('Store_table_seat-', '').replace('-tableseat', '')
                table_seat_id = request.POST[key]
                if table_seat_id != '':
                    table_seat = TableSeat.objects.get(pk=table_seat_id).table_seat
                    if 'Store_table_seat-' + id + '-DELETE' in request.POST:
                        if request.POST['Store_table_seat-' + id + '-DELETE'] == 'on':
                            StoreTableStatus.objects.filter(store=obj, table_seat=table_seat).delete()
                    else:
                        try:
                            StoreTableStatus.objects.get(store=obj, table_seat=table_seat)
                        except:
                            store_table_status = StoreTableStatus(store=obj, table_seat=table_seat, status=StoreTableStatus.OPEN)
                            store_table_status.save()

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        formset.save()


class CompanyAdmin(admin.ModelAdmin):
    pass


admin.site.register(ServiceItem, ServiceItemAdmin)
admin.site.register(TableSeat, TableSeatAdmin),
admin.site.register(DiningType, DiningTypeAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Company, CompanyAdmin)
