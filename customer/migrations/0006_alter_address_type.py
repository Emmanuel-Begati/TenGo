# Generated by Django 5.0.6 on 2024-07-11 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_address_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='type',
            field=models.CharField(choices=[('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other')], default='Home', max_length=10),
        ),
    ]