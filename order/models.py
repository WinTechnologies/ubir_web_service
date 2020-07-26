from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from datetime import datetime

from customer.models import Customer
from store.models import Store, ServiceItem


@python_2_unicode_compatible
class Order(models.Model):
    PENDING = 'PENDING'
    INPROGRESS = 'INPROGRESS'
    COMPLETED = 'COMPLETED'

    CHOICES = (
        (PENDING, PENDING),
        (INPROGRESS, INPROGRESS),
        (COMPLETED, COMPLETED)
    )
    CHOICES_DICT = dict(CHOICES)

    record_number = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    table_id = models.CharField(max_length=25, null=True, blank=True)
    service_item = models.ForeignKey(ServiceItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    start_time = models.DateTimeField(default=datetime.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=CHOICES, default=PENDING, max_length=25)

    def __str__(self):
        return f"Store {self.store.store_id} - Table {self.table_id} - {self.service_item.title} - {self.status}"
