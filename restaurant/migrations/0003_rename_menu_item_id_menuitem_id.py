# Generated by Django 5.0.6 on 2024-07-01 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='menu_item_id',
            new_name='id',
        ),
    ]
