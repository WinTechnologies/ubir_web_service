# Generated by Django 2.2.4 on 2020-07-26 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='is_in_store',
            field=models.BooleanField(default=False, verbose_name='True if a customer is already logged in, False if not'),
        ),
    ]