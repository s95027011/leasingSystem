from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
import uuid

from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

# define Product type
class Type(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

# define Product
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

    def __str__(self):
        return self.product_name

# define Item
class Item(models.Model):
    ITEM_STATUS = (
        ('0', '上架'),   # update
        ('1', '已出租'),
        ('2', '未上架'),   # create  
        ('3', '下架'), # delete
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True)
    item_status = models.CharField(
        max_length=1,
        choices=ITEM_STATUS,
        default='2',
        help_text='Item 狀態')

    def __str__(self):
        return self.product.__str__()

# define transaction table
class Transaction(models.Model):
    # 交易方式
    PAYMENT_METHOD = (
        ('c', '信用卡'),
    )

    CARD_TYPE = (
        ('v', 'VISA'),
        ('m', 'Master')
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
    card_type = models.CharField(choices=CARD_TYPE, max_length=1)
    card_id = models.CharField(max_length=16, validators=[
        MinLengthValidator(16)], blank=True)
    dueD_date = models.CharField(max_length=4, validators=[
        MinLengthValidator(4)], blank=True)


# define Member
class Member(models.Model):
    SEX = (('0', '女性'), ('1', '男性'), ('2', '不選擇'))
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    #member_name = models.CharField(blank=False, max_length=20)
    member_sex = models.CharField(choices=SEX, max_length=1, help_text='輸入性別')
    member_addr = models.CharField(blank=False, max_length=50)
    #member_email = models.EmailField(max_length=254)
    member_birth = models.DateField(blank=True)
    #member_phone = PhoneNumberField(blank=False)

    
    # member_register_date = models.DateField(auto_now_add=timezone.now)
   # member_login = models.DateField(auto_now_add=timezone.now)  # 現在登入時間
   # member_pwd = models.CharField(max_length=20)
    # Password in django https://stackoverflow.com/questions/17523263/how-to-create-password-field-in-model-django

# define Cart
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    member = models.OneToOneField(Member, on_delete=models.SET_NULL, null=True)
    product = models.ManyToManyField(Product)
    cart_count = models.PositiveIntegerField()


# define Order
class Order(models.Model):
    ORDER_STATUS = (('0', '配送中'), ('1', '尚未配送'), ('2', '已送達'))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True)
    member = models.ForeignKey(
        'Member', on_delete=models.SET_NULL, null=True)
    item = models.ManyToManyField(Item)
    order_time = models.DateTimeField(auto_now_add=timezone.now)
    rent_time = models.DateTimeField(auto_now_add=timezone.now)
    order_status = models.CharField(
        choices=ORDER_STATUS, max_length=1, help_text='商品狀態')
    order_price = models.PositiveIntegerField()
    return_time = models.TimeField()


# define DueRecord
class Duerecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    due_day = models.DateField(auto_now_add=timezone.now)

