# Generated by Django 5.0.6 on 2024-07-01 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_rename_menu_item_id_menuitem_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='id',
            new_name='menu_item_id',
        ),
    ]
