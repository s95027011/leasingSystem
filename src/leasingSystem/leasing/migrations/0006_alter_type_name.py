# Generated by Django 4.1.3 on 2022-12-09 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0005_alter_item_item_status_alter_transaction_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='type',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]