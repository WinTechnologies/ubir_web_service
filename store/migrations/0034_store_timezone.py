# Generated by Django 2.2.4 on 2020-10-27 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_auto_20200925_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='timezone',
            field=models.CharField(default='UTC', max_length=50),
        ),
    ]
