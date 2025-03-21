# Generated by Django 4.2.19 on 2025-02-13 16:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inmaticpart2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(max_length=255)),
                ('concept', models.TextField()),
                ('base_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('vat', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField(default=datetime.date.today)),
                ('state', models.CharField(default='DRAFT2', max_length=20)),
            ],
        ),
    ]
