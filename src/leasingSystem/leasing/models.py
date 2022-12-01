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

    name = models.CharField(max_length=20)
    product_size = models.CharField(
        max_length=2, 
        choices=PRODUCT_SIZE, 
        default='m', 
        help_text='服裝尺碼')
    product_type = models.ManyToManyField(Type, help_text='服裝類型') # 多對多?
    price = models.PositiveIntegerField()
    fine = models.PositiveIntegerField()
#### #### #### #### #### #### #### ####


#### #### #### #### #### #### #### ####
# define Item
class Item(models.Model):
    ITEM_STATUS = (

    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
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
        default='c', # 預設信用卡
        help_text='選擇付款方式',
    )
    trans_time = models.DateTimeField(auto_now_add=timezone.now) # 現在時區時間

    # CardInfo
    # 銀行7碼 (前三法 銀行, 後四碼 分支機構)
    bankId = models.CharField(max_length=7, validators=[MinLengthValidator(7)], blank=True) 
    # Card Type ?
    cardType = models.CharField()
    cardID = models.CharField(max_length=16, validators=[MinLengthValidator(16)], blank=True)
    dueDate = models.CharField(max_length=4, validators=[MinLengthValidator(4)], blank=True)
#### #### #### #### #### #### #### ####

#### #### #### #### #### #### #### ####
# defin Member
#### #### #### #### #### #### #### ####

#### #### #### #### #### #### #### ####
# defin Cart
#### #### #### #### #### #### #### ####

#### #### #### #### #### #### #### ####
# defin Order
#### #### #### #### #### #### #### ####

#### #### #### #### #### #### #### ####
# defin DueRecord
#### #### #### #### #### #### #### ####
