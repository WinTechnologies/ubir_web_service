from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from service.models import Serviceman


@python_2_unicode_compatible
class Message(models.Model):
    QUESTION = 'QUESTION'
    ANSWER = 'ANSWER'
    CHOICES = (
        (QUESTION, QUESTION),
        (ANSWER, ANSWER)
    )
    CHOICES_DICT = dict(CHOICES)
    record_number = models.AutoField(primary_key=True)
    store_id = models.CharField(max_length=25, null=True, blank=True, verbose_name="Store ID")
    type = models.CharField(choices=CHOICES, max_length=25, null=True, blank=True)
    table_id = models.CharField(max_length=25, null=True, blank=True, verbose_name="Table Seat Number")
    phone = models.CharField(max_length=15, null=True, blank=True)
    item_title = models.CharField(max_length=150, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    session_token = models.CharField(max_length=512, null=True, blank=True)
    is_seen = models.BooleanField(default=False)
    flash = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.type} - Table {self.table_id} - {self.item_title} - {self.message}"
