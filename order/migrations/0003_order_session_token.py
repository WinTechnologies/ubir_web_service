# Generated by Django 2.2.4 on 2020-08-28 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20200805_0034'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='session_token',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
