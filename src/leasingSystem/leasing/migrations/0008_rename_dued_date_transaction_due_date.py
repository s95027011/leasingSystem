# Generated by Django 4.1.3 on 2022-12-10 02:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0007_rename_cart_count_cart_product_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='dueD_date',
            new_name='due_date',
        ),
    ]