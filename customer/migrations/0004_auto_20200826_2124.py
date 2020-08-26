# Generated by Django 2.2.4 on 2020-08-26 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_auto_20200821_0144'),
        ('customer', '0003_auto_20200822_0314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='dining_type',
        ),
        migrations.AddField(
            model_name='customer',
            name='dining_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.DiningType'),
        ),
    ]
