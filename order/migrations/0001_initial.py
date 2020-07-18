# Generated by Django 2.2.4 on 2020-07-18 01:58

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('record_number', models.AutoField(primary_key=True, serialize=False)),
                ('table_id', models.CharField(blank=True, max_length=25, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('start_time', models.DateTimeField(default=datetime.datetime.now)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('INPROGRESS', 'INPROGRESS'), ('COMPLETED', 'COMPLETED')], default='PENDING', max_length=25)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.Customer')),
                ('service_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.ServiceItem')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Store')),
            ],
        ),
    ]
