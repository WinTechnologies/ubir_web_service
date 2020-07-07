from django import forms
from django.contrib import admin
from .models import ServiceItem, StoreServiceItem, Store, Company


# class StoreServiceItemAdminForm(forms.ModelForm):
#     service_item = forms.ModelMultipleChoiceField(queryset=ServiceItem.objects.order_by('order'))
#
#     class Meta:
#         model = StoreServiceItem
#         fields = '__all__'
#
#
# class StoreServiceItemAdmin(admin.ModelAdmin):
#     form = StoreServiceItemAdminForm


class MembershipInline(admin.TabularInline):
    model = StoreServiceItem.service_item.through


class ServiceItemAdmin(admin.ModelAdmin):
    pass


class StoreServiceItemAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    exclude = ('service_item',)


class StoreAdmin(admin.ModelAdmin):
    pass


class CompanyAdmin(admin.ModelAdmin):
    pass


admin.site.register(StoreServiceItem, StoreServiceItemAdmin)
admin.site.register(ServiceItem, ServiceItemAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Company, CompanyAdmin)
