# Generated by Django 5.0.7 on 2024-07-16 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0007_order_is_visible_to_restaurant'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='reference',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
