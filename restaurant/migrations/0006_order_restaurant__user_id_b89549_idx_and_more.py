# Generated by Django 5.1.1 on 2025-06-28 13:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0003_initial'),
        ('restaurant', '0005_menuitem_primary_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['user', 'payment_status'], name='restaurant__user_id_b89549_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['restaurant', 'is_visible_to_restaurant'], name='restaurant__restaur_1ef6c5_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='restaurant__status_d66ca5_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_time'], name='restaurant__order_t_5ec1f8_idx'),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['owner'], name='restaurant__owner_i_a0af92_idx'),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['is_open', 'rating'], name='restaurant__is_open_8624f3_idx'),
        ),
        migrations.AddIndex(
            model_name='restaurant',
            index=models.Index(fields=['delivery_time'], name='restaurant__deliver_3cef53_idx'),
        ),
    ]
