# Generated by Django 4.1.3 on 2022-12-17 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leasing", "0011_merge_20221217_2312"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="order_time",
            new_name="order_datetime",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="rent_time",
            new_name="rent_datetime",
        ),
        migrations.AlterField(
            model_name="member",
            name="member_phone",
            field=models.CharField(max_length=10),
        ),
    ]