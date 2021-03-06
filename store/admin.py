from django.contrib import admin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from .models import ServiceItem, TableSeat, Store, DiningType, Company


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

    def save_related(self, request, form, formsets, change):
        super(StoreAdmin, self).save_related(request, form, formsets, change)
        obj = form.instance
        for table_seat in obj.table_seat.all():
            if not obj.store_id + '.' in table_seat.table_id:
                obj.table_seat.remove(table_seat)
        obj.save()

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
