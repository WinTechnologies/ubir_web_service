# Generated by Django 2.2.4 on 2020-08-11 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_store_sms_text_guest_alert'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='screen_flash',
            field=models.BooleanField(default=False, verbose_name='Screen Flash'),
        ),
    ]