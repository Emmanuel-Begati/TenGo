# Generated by Django 5.0.6 on 2024-07-11 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_alter_address_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
    ]
