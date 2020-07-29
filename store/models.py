
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


class Company(models.Model):
    company_id = models.IntegerField(verbose_name="Company Id", unique=True)
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Company Name")
    description = models.TextField(null=True, blank=True, verbose_name="Company Overview")

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f"{self.name} - {self.company_id}"


class ServiceItem(models.Model):
    title = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = 'Service Item'
        verbose_name_plural = 'Service Items'

    def __str__(self):
        return self.title


class TableSeat(models.Model):
    table_seat = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = 'Table/Seat'
        verbose_name_plural = 'Tables/Seats'

    def __str__(self):
        return self.table_seat


class Store(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    store_id = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Store Name")
    timer_turn_yellow = models.IntegerField(default=5, verbose_name="Service Timer Turn Yellow (in mins)")
    timer_turn_red = models.IntegerField(default=10, verbose_name="Service Timer Turn Red (in mins)")
    timer_escalation_to_manager = models.IntegerField(default=12, verbose_name="Escalation to manager (in mins)")
    logo = models.ImageField(upload_to='uploads/', blank=True, verbose_name="Store Logo Image")
    order_url = models.TextField(null=True, blank=True, verbose_name="Place New Order URL")
    service_item = models.ManyToManyField(ServiceItem, blank=True, related_name='store_service_item')
    table_seat = models.ManyToManyField(TableSeat, blank=True, related_name='store_table_seat')

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        if not self.store_id.startswith("{}.".format(self.company.company_id)):
            raise ValidationError({"store_id": "Store ID should start with '{Company ID}.'"})


class StoreTableStatus(models.Model):
    OPEN = 'Open'
    CLOSED = 'Closed'
    CHOICES = (
        (OPEN, OPEN),
        (CLOSED, CLOSED),
    )
    CHOICES_DICT = dict(CHOICES)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    table_seat = models.CharField(max_length=10, unique=True)
    status = models.CharField(choices=CHOICES, default=OPEN, max_length=25)

    class Meta:
        verbose_name = 'Table/Seat'
        verbose_name_plural = 'Tables/Seats'

    def __str__(self):
        return self.table_seat


@receiver(post_save, sender=Store)
def create_store(sender, instance, created, **kwargs):
    table_seats = instance.table_seat.all()
    for table_seat in table_seats:
        try:
            StoreTableStatus.objects.get(store=instance, table_seat=table_seat.table_seat)
        except:
            store_table_status = StoreTableStatus(store=instance, table_seat=table_seat.table_seat, status=StoreTableStatus.OPEN)
            store_table_status.save()
