# Generated by Django 2.2.4 on 2020-09-11 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0021_auto_20200911_2147'),
    ]

    operations = [
        migrations.AddField(
            model_name='diningtype',
            name='action_type',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Action Type'),
        ),
    ]
