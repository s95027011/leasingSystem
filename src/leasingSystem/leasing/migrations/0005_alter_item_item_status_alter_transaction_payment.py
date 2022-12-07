# Generated by Django 4.1.3 on 2022-12-07 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0004_alter_member_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='item_status',
            field=models.CharField(choices=[('0', '上架'), ('1', '已出租'), ('2', '未上架'), ('3', '下架')], default='2', help_text='Item 狀態', max_length=1),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='payment',
            field=models.CharField(choices=[('c', '信用卡')], default='c', help_text='選擇付款方式', max_length=1),
        ),
    ]
