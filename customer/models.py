from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _
from datetime import datetime


@python_2_unicode_compatible
class Customer(models.Model):
    record_number = models.AutoField(primary_key=True)
    company_id = models.IntegerField(null=True, blank=True)
    store_id = models.CharField(max_length=25, null=True, blank=True)
    table_id = models.CharField(max_length=25, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    session_token = models.CharField(max_length=512, null=True, blank=True)
    start_time = models.DateTimeField(default=datetime.now)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.record_number} <-> {self.phone}"


@python_2_unicode_compatible
class UBIRWiFi(models.Model):
    record_number = models.AutoField(primary_key=True)
    id = models.IntegerField(null=True, blank=True)
    operator = models.CharField(max_length=25, null=True, blank=True)
    location_id = models.IntegerField(null=True, blank=True)
    user_name = models.CharField(max_length=25, null=True, blank=True)
    action_date_gmt = models.DateTimeField(default=datetime.now)
    package_id = models.CharField(max_length=25, null=True, blank=True)
    user_agent = models.CharField(max_length=250, null=True, blank=True)
    customer = models.CharField(max_length=25, null=True, blank=True)
    newsletter = models.IntegerField(null=True, blank=True)
    company_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(_('email address'))
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=25, null=True, blank=True)
    zip = models.CharField(max_length=25, null=True, blank=True)
    country_code = models.CharField(max_length=25, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    q1 = models.CharField(max_length=50, null=True, blank=True)
    a1 = models.CharField(max_length=50, null=True, blank=True)
    q2 = models.CharField(max_length=50, null=True, blank=True)
    a2 = models.CharField(max_length=50, null=True, blank=True)
    q3 = models.CharField(max_length=50, null=True, blank=True)
    a3 = models.CharField(max_length=50, null=True, blank=True)
    q4 = models.CharField(max_length=50, null=True, blank=True)
    a4 = models.CharField(max_length=50, null=True, blank=True)
    q5 = models.CharField(max_length=50, null=True, blank=True)
    a5 = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'UBIR WiFi Login History'
        verbose_name_plural = 'UBIR WiFi Login Histories'

    def __str__(self):
        return f"{self.id} - {self.phone}"
