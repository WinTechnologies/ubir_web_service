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
        verbose_name = _('Serviceman')
        verbose_name_plural = _('Servicemen')

    def __str__(self):
        return self.user.username
