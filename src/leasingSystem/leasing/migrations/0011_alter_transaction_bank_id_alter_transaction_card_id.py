# Generated by Django 4.1.3 on 2022-12-13 12:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0010_transaction_valid_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='bank_id',
            field=models.CharField(blank=True, help_text='前三碼 銀行, 後四碼 分支機構', max_length=7, validators=[django.core.validators.MinLengthValidator(7)]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='card_id',
            field=models.CharField(blank=True, help_text='14碼', max_length=14, validators=[django.core.validators.MinLengthValidator(14)]),
        ),
    ]