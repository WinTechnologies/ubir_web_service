import pytz
import django.utils.timezone
from datetime import datetime
from django.db import models
from django.db.models.signals import post_save
from django_better_admin_arrayfield.models.fields import ArrayField

from django.dispatch import receiver
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from store.constants import TIMEZONES


class Company(models.Model):
    company_id = models.IntegerField(verbose_name="Company Id", unique=True)
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Company Name")
    description = models.TextField(null=True, blank=True, verbose_name="Company Overview")
    specific_phone_number_prefix = models.CharField(max_length=25, default='', verbose_name="Specific Phone Number Prefix")

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return f"{self.name} - {self.company_id}"


class ServiceItem(models.Model):
    title = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Service Item"
        verbose_name_plural = "Service Items"

    def __str__(self):
        return self.title


class DiningType(models.Model):
    title = models.CharField(max_length=150, unique=True)
    action_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="Action Type")

    class Meta:
        verbose_name = "Dining Type"
        verbose_name_plural = "Dining Types"

    def __str__(self):
        return self.title


class TableSeat(models.Model):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    CLEANING = "Cleaning"
    ACTION_STATUS_CHOICES = (
        (AVAILABLE, AVAILABLE),
        (OCCUPIED, OCCUPIED),
        (CLEANING, CLEANING),
    )
    ACTION_STATUS_CHOICES_DICT = dict(ACTION_STATUS_CHOICES)
    OPEN = "Open"
    CLOSED = "Closed"
    STATUS_CHOICES = (
        (OPEN, OPEN),
        (CLOSED, CLOSED),
    )
    STATUS_CHOICES_DICT = dict(STATUS_CHOICES)
    table_id = models.CharField(max_length=25,
                                verbose_name="Unique Table ID(Format: {Store#}.{Table/Seat} (for example, 1.1.1 or 1.1.B1))",
                                null=True, blank=True)
    table_seat = models.CharField(max_length=10, verbose_name="Pure Table/Seat Name(For example, 1 or B1)", null=True,
                                  blank=True)
    action_status = models.CharField(choices=ACTION_STATUS_CHOICES, default=AVAILABLE, max_length=25)
    status = models.CharField(choices=STATUS_CHOICES, default=OPEN, max_length=25)
    location = models.ForeignKey(DiningType, on_delete=models.CASCADE, null=True, blank=True)
    seats = models.IntegerField(default=1, verbose_name="Number of Seats")
    last_time_status_changed = models.DateTimeField(default=datetime.now, verbose_name="Last time table status changed",
                                                    null=True, blank=True)
    seated_time = models.DateTimeField(default=datetime.now, verbose_name="Actual time table is seated", null=True,
                                       blank=True)
    ordered_time = models.DateTimeField(default=datetime.now, verbose_name="Actual time order is received", null=True,
                                        blank=True)
    last_time_customer_tap = models.DateTimeField(default=datetime.now, verbose_name="Last time customer tapped",
                                                  null=True, blank=True)

    class Meta:
        verbose_name = "Table/Seat"
        verbose_name_plural = "Tables/Seats"

    def __str__(self):
        if self.table_id:
            return self.table_id
        else:
            return self.table_seat

    def clean(self):
        validation = False
        for store in Store.objects.all():
            if store.store_id + '.' in self.table_id:
                validation = True
        if not validation:
            raise ValidationError({"table_id": "It must contain the store #. (for example. store#.table/seat name)"})
        if self.table_id.split('.')[-1] != self.table_seat:
            raise ValidationError({"table_seat": "It does not match with the table_id"})


class Store(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    store_id = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Store Name")
    timer_turn_yellow = models.IntegerField(default=5, verbose_name="Service Timer Turn Yellow (in mins)")
    timer_turn_red = models.IntegerField(default=10, verbose_name="Service Timer Turn Red (in mins)")
    timer_escalation_to_manager = models.IntegerField(default=12, verbose_name="Escalation to manager (in mins)")
    logo = models.ImageField(upload_to="uploads/", blank=True, verbose_name="Store Logo Image")
    order_url = models.TextField(null=True, blank=True, verbose_name="Place New Order URL")
    survey_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="Survey URL")
    sms_text_guest_alert = models.BooleanField(default=False, verbose_name="SMS Text Guest Alert")
    screen_flash = models.BooleanField(default=False, verbose_name="Screen Flash")
    service_item = models.ManyToManyField(ServiceItem, blank=True, related_name="store_service_item")
    table_seat = models.ManyToManyField(TableSeat, blank=True, related_name="store_table_seat")
    dining_type = models.ManyToManyField(DiningType, blank=True, related_name="store_dining_type")
    ip_addresses = ArrayField(models.CharField(max_length=20), blank=True, null=True, verbose_name="IP Addresses")
    order_rank = models.IntegerField(null=True, blank=True, verbose_name="Order Rank# (0 indicates that 'Place a New Order' button is shown at all times)")
    wait_time_frame = models.IntegerField(default=10, verbose_name="Wait Time Frame for getting longest/average wait time")
    pickup_message = models.CharField(max_length=100, default='', verbose_name="Message for 'Pickup & Bar' type")
    curside_message = models.CharField(max_length=100, default='',
                                       verbose_name="Message for 'Delivering to Car/Curbside' type")
    timezone = models.CharField(choices=TIMEZONES, default='UTC', max_length=50)

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"

    def __str__(self):
        return f"{self.name}"

    def validateIP(self, IP):
        """
        :type IP: str
        :rtype: str
        """
        def isIPv4(s):
            try:
                return str(int(s)) == s and 0 <= int(s) <= 255
            except:
                return False
        def isIPv6(s):
            if len(s) > 4:
                return False
            try:
                return int(s, 16) >= 0 and s[0] != '-'
            except:
                return False
        if IP.count(".") == 3 and all(isIPv4(i) for i in IP.split(".")):
            return True
        if IP.count(":") == 7 and all(isIPv6(i) for i in IP.split(":")):
            return True
        return False

    def clean(self):
        django.utils.timezone.activate(pytz.timezone(self.timezone))
        if not self.store_id.startswith("{}.".format(self.company.company_id)):
            raise ValidationError({"store_id": "Store ID should start with '{Company ID}.'"})
        ip_address_valid = True
        if self.ip_addresses:
            for ip_address in self.ip_addresses:
                if not self.validateIP(ip_address):
                    ip_address_valid = False
        if not ip_address_valid:
            raise ValidationError({"ip_addresses": "IP Address is in invalid format."})
