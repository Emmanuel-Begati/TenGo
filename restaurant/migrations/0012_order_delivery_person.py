# Generated by Django 5.0.7 on 2024-07-27 00:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0002_rename_delivery_time_delivery_accepted_at_and_more'),
        ('restaurant', '0011_remove_deliveryperson_user_delete_delivery_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='delivery.deliveryperson'),
        ),
    ]