# Generated by Django 2.2.4 on 2020-08-28 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_message_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='session_token',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
