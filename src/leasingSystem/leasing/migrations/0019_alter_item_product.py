# Generated by Django 3.2.16 on 2022-12-14 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0018_alter_item_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='leasing.product'),
        ),
    ]