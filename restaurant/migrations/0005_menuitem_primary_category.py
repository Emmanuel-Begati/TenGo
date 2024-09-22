# Generated by Django 5.0.7 on 2024-09-19 21:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0004_remove_menuitem_category_menuitem_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='primary_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_menu_items', to='restaurant.category'),
        ),
    ]