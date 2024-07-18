# Generated by Django 5.0.7 on 2024-07-18 02:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0009_remove_menuitem_menu'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='restaurant.menu'),
        ),
    ]
