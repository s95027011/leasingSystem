# Generated by Django 4.1.3 on 2022-12-13 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0014_remove_cart_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='product',
            field=models.ManyToManyField(to='leasing.product'),
        ),
    ]