# Generated by Django 5.0.6 on 2024-07-15 18:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0002_remove_restaurant_email_address_restaurant_related_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Address',
            new_name='RestaurantAddress',
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='restaurant', to='restaurant.restaurantaddress'),
        ),
    ]