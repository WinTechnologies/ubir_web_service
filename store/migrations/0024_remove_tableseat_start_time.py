# Generated by Django 2.2.4 on 2020-09-14 16:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0023_tableseat_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tableseat',
            name='start_time',
        ),
    ]
