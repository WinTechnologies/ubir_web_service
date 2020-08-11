from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _
from users.models import User
from store.models import Store


@python_2_unicode_compatible
class Serviceman(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Staff')
        verbose_name_plural = _('Staff')

    def __str__(self):
        return self.user.username


@python_2_unicode_compatible
class ServicemanConfig(models.Model):
    serviceman = models.ForeignKey(Serviceman, on_delete=models.CASCADE, verbose_name="Service Person")
    table_seat = models.CharField(max_length=10)

    class Meta:
        verbose_name = _('Service Person Config')
        verbose_name_plural = _('Service Person Config')

    def __str__(self):
        return f"{self.serviceman.user.username} - {self.table_seat}"
