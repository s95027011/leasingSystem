# Generated by Django 4.1.3 on 2022-12-18 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0012_rename_order_time_order_order_datetime_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='item_size',
        ),
        migrations.AddField(
            model_name='product',
            name='product_size',
            field=models.CharField(choices=[('S', 'small'), ('M', 'medium'), ('L', 'large'), ('XL', 'extra large')], default='m', help_text='服裝尺碼', max_length=2),
        ),
    ]