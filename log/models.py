from datetime import datetime
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class CustomerLog(models.Model):
    record_number = models.AutoField(primary_key=True)
    company = models.CharField(max_length=25, blank=True, null=True, verbose_name="Company Name")
    store = models.CharField(max_length=25, blank=True, null=True, verbose_name="Store Name")
    login = models.CharField(max_length=25, blank=True, null=True, verbose_name="Customer Phone Number")
    tap = models.CharField(max_length=25, blank=True, null=True, verbose_name="Tap")
    content = models.CharField(max_length=500, blank=True, null=True, verbose_name="Content")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Customer Log"
        verbose_name_plural = "Customer Logs"

    def __str__(self):
        return f"{self.company} - {self.store} - {self.login} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.tap} - {self.content}"


@python_2_unicode_compatible
class ServiceLog(models.Model):
    record_number = models.AutoField(primary_key=True)
    company = models.CharField(max_length=25, blank=True, null=True, verbose_name="Company Name")
    store = models.CharField(max_length=25, blank=True, null=True, verbose_name="Store Name")
    login = models.CharField(max_length=25, blank=True, null=True, verbose_name="Staff Username")
    tap = models.CharField(max_length=25, blank=True, null=True, verbose_name="Tap")
    content = models.CharField(max_length=500, blank=True, null=True, verbose_name="Content")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Service Log"
        verbose_name_plural = "Service Logs"

    def __str__(self):
        return f"{self.company} - {self.store} - {self.login} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.tap} - {self.content}"
