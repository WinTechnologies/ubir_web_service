# Generated by Django 2.2.4 on 2020-08-17 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerlog',
            name='content',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Content'),
        ),
    ]
