# Generated by Django 2.2.4 on 2020-07-29 19:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServicemanConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_seat', models.CharField(max_length=10)),
                ('serviceman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.Serviceman', verbose_name='Service Person')),
            ],
            options={
                'verbose_name': 'Service Person Config',
                'verbose_name_plural': 'Service Person Config',
            },
        ),
    ]