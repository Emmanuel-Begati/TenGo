from django.db import migrations, models

def forwards_func(apps, schema_editor):
    MenuItem = apps.get_model("restaurant", "MenuItem")
    db_alias = schema_editor.connection.alias
    MenuItem.objects.using(db_alias).all().update(menu_item_id=models.F('id'))

class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_remove_menuitem_customer_orders'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='menu_item_id',
            field=models.IntegerField(unique=True, blank=True, null=True),
        ),
        migrations.RunPython(forwards_func),
    ]