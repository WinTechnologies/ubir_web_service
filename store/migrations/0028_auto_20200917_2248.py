# Generated by Django 2.2.4 on 2020-09-17 22:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0027_auto_20200917_2245'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tableseat',
            old_name='status',
            new_name='action_status',
        ),
    ]
