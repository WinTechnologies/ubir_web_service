# Generated by Django 2.2.4 on 2020-08-26 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_auto_20200821_0144'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='order_rank',
            field=models.IntegerField(blank=True, null=True, verbose_name="0 indicates that 'Place a New Order' button is shown at all times"),
        ),
    ]
