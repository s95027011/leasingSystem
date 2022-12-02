from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
import uuid

# Create your models here.

#### #### #### #### #### #### #### ####
# define Product type


class Type(models.Model):
    name = models.CharField(max_length=20)
#### #### #### #### #### #### #### ####


#### #### #### #### #### #### #### ####
# defin Product
class Product(models.Model):
    # 商品規格
    PRODUCT_SIZE = (
        ('S', 'small'),
        ('M', 'medium'),
        ('L', 'large'),
        ('XL', 'extra large'),
    )

    product_name = models.CharField(max_length=20)
    product_size = models.CharField(
        max_length=2,
        choices=PRODUCT_SIZE,
        default='m',
        help_text='服裝尺碼')
    product_type = models.ManyToManyField(Type, help_text='服裝類型')  # 多對多?
    product_price = models.PositiveIntegerField()
    product_fine = models.PositiveIntegerField()
#### #### #### #### #### #### #### ####


#### #### #### #### #### #### #### ####
# define Item
class Item(models.Model):
    ITEM_STATUS = (

    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True)
    item_status = models.CharField(
        max_length=1,
        choices=ITEM_STATUS,
        help_text='Item 狀態')
#### #### #### #### #### #### #### ####


#### #### #### #### #### #### #### ####
# define transaction table
class Transaction(models.Model):
    # 交易方式
    PAYMENT_METHOD = (
        ('c', '信用卡')
        ('t', '轉帳'),
    )

    # Transaction Info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    payment = models.CharField(
        max_length=1,
        choices=PAYMENT_METHOD,
        default='c',  # 預設信用卡
        help_text='選擇付款方式',
    )
    trans_time = models.DateTimeField(auto_now_add=timezone.now)  # 現在時區時間

    # CardInfo
    # 銀行7碼 (前三法 銀行, 後四碼 分支機構)
    bank_id = models.CharField(max_length=7, validators=[
        MinLengthValidator(7)], blank=True)
    # Card Type ?
    card_type = models.CharField()
    card_id = models.CharField(max_length=16, validators=[
        MinLengthValidator(16)], blank=True)
    dueD_date = models.CharField(max_length=4, validators=[
        MinLengthValidator(4)], blank=True)
#### #### #### #### #### #### #### ####


#### #### #### #### #### #### #### ####
# defin Member
class Member(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    member_name = models.CharField(blank=False)
    member_sex = models.CharField(blank=True)
    member_addr = models.CharField(blank=False)
    member_email = models.EmailField(max_length=254)
    member_birth = models.DateField(blank=True)
    member_phone = models.PhoneNumberField(blank=False)
    member_register_date = models.DateField(auto_now_add=timezone.now)
    member_login = models.DateField(auto_now_add=timezone.now)  # 現在登入時間
    member_pwd = models.CharField(max_length=20)
    # Password in django https://stackoverflow.com/questions/17523263/how-to-create-password-field-in-model-django
#### #### #### #### #### #### #### ####

#### #### #### #### #### #### #### ####
# defin Cart


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    cart_count = models.PositiveIntegerField()
#### #### #### #### #### #### #### ####

#### #### #### #### #### #### #### ####
# defin Order


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order_time = models.TimeField(auto_now_add=timezone.now)
    rent_time = models.TimeField()
    order_status = models.CharField()
    order_price = models.PositiveIntegerField()
    return_time = models.TimeField()
#### #### #### #### #### #### #### ####

#### #### #### #### #### #### #### ####
# defin DueRecord
#### #### #### #### #### #### #### ####
