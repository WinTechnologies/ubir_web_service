from uuid import uuid4

from django.db import models


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class Company(models.Model):
    company_id = models.IntegerField(verbose_name="Company Id", unique=True)
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Company Name")
    description = models.TextField(null=True, blank=True, verbose_name="Company Overview")

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f"{self.name}"


class Store(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    store_id = models.CharField(max_length=25, null=True, blank=True)
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Store Name")
    timer_turn_yellow = models.IntegerField(default=5, verbose_name="Service Timer Turn Yellow (in mins)")
    timer_turn_red = models.IntegerField(default=10, verbose_name="Service Timer Turn Red (in mins)")
    timer_escalation_to_manager = models.IntegerField(default=12, verbose_name="Escalation to manager (in mins)")
    logo = models.ImageField(upload_to='uploads/', blank=True, verbose_name="Store Logo Image")
    order_url = models.TextField(null=True, blank=True, verbose_name="Place New Order URL")

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return f"{self.name}"


class ServiceItem(models.Model):
    title = models.CharField(max_length=150)
    order = models.IntegerField()

    class Meta:
        verbose_name = 'Service Item'
        verbose_name_plural = 'Service Items'

    def __str__(self):
        return self.title


class StoreServiceItem(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    service_item = models.ManyToManyField(ServiceItem, blank=True, related_name='store_service_item')

    class Meta:
        verbose_name = 'Store Service Item'
        verbose_name_plural = 'Store Service Items'

    def __str__(self):
        return f"{self.store.name}"
