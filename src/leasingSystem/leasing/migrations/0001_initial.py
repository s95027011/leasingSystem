# Generated by Django 4.1.3 on 2022-12-14 09:00

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('item_status', models.CharField(choices=[('0', '上架'), ('1', '已出租'), ('2', '未上架'), ('3', '下架')], default='2', help_text='Item 狀態', max_length=1)),
                ('item_size', models.CharField(choices=[('S', 'small'), ('M', 'medium'), ('L', 'large'), ('XL', 'extra large')], default='m', help_text='服裝尺碼', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_sex', models.CharField(choices=[('0', '女性'), ('1', '男性'), ('2', '不選擇')], help_text='輸入性別', max_length=1)),
                ('member_addr', models.CharField(max_length=50)),
                ('member_birth', models.DateField(blank=True)),
                ('member_phone', models.CharField(max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('order_time', models.DateTimeField(auto_now_add=True)),
                ('rent_time', models.DateTimeField()),
                ('order_status', models.CharField(choices=[('0', '配送中'), ('1', '尚未配送'), ('2', '已送達')], help_text='商品狀態', max_length=1)),
                ('return_time', models.DateTimeField()),
                ('item', models.ManyToManyField(to='leasing.item')),
                ('member', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='leasing.member')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('payment', models.CharField(choices=[('c', '信用卡')], default='c', help_text='選擇付款方式', max_length=1)),
                ('trans_time', models.DateTimeField(auto_now_add=True)),
                ('bank_id', models.CharField(blank=True, help_text='前三碼 銀行, 後四碼 分支機構', max_length=7, validators=[django.core.validators.MinLengthValidator(7)])),
                ('card_type', models.CharField(choices=[('v', 'VISA'), ('m', 'Master')], max_length=1)),
                ('card_id', models.CharField(blank=True, help_text='16碼', max_length=16, validators=[django.core.validators.MinLengthValidator(16)])),
                ('due_date', models.CharField(blank=True, max_length=4, validators=[django.core.validators.MinLengthValidator(4)])),
                ('valid_number', models.CharField(blank=True, max_length=3, validators=[django.core.validators.MinLengthValidator(3)])),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReturnRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('due_date', models.DateTimeField(auto_now=True)),
                ('is_due', models.BooleanField(default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leasing.order')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=20)),
                ('product_price', models.PositiveIntegerField()),
                ('product_fine', models.PositiveIntegerField()),
                ('product_image', models.CharField(default='', help_text='圖片路徑', max_length=255)),
                ('product_description', models.TextField(blank=True, help_text='產品描述', null=True)),
                ('product_type', models.ManyToManyField(help_text='服裝類型', to='leasing.type')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='transaction',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='leasing.transaction'),
        ),
        migrations.AddField(
            model_name='item',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='leasing.product'),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('product_count', models.PositiveIntegerField()),
                ('member', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='leasing.member')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='leasing.product')),
            ],
        ),
    ]
