# Generated by Django 4.1.3 on 2022-12-14 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0015_cart_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_description',
            field=models.TextField(blank=True, help_text='產品描述', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='product_image',
            field=models.CharField(default='', help_text='圖片路徑', max_length=255),
        ),
    ]