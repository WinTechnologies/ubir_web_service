# Generated by Django 2.2.4 on 2020-07-29 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_storetablestatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storetablestatus',
            name='status',
            field=models.CharField(choices=[('Open', 'Open'), ('Closed', 'Closed')], default='Open', max_length=25),
        ),
    ]
