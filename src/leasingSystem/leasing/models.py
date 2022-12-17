from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.

# define Product type

def only_int(value):
    if not value.isdigit():
        raise ValidationError('只能輸入數字')

class Type(models.Model):
    name = models.CharField(max_length=20, unique=True)

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
    product_image = models.CharField(
        max_length=255, help_text='圖片路徑', default='')
    product_description = models.TextField(
        help_text='產品描述', blank=True, null=True)

    def __str__(self):
        return self.product_name
    
# define Item


class Item(models.Model):
    ITEM_STATUS = (
        ('0', '上架'),   # update
        ('1', '已出租'),
        ('2', '未上架'),   # create
        ('3', '下架'),  # delete
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE)
    item_status = models.CharField(
        max_length=1,
        choices=ITEM_STATUS,
        default='2',
        help_text='Item 狀態')

    def __str__(self):
        return self.product.__str__() + ' (' + str(self.id) + ')'

    def get_available_product_count(self, product_id):
        return Item.objects.filter(product_id=product_id).filter(item_status='0').count()

    def get_item_status(self):
        return self.item_status

    def set_item_stauts(self, status):
        self.item_status = status
        self.save()

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
    # 銀行7碼 (前三碼 銀行, 後四碼 分支機構)
    bank_id = models.CharField(max_length=7, validators=[
        MinLengthValidator(7), only_int], blank=True, help_text='前三碼 銀行, 後四碼 分支機構')
    # Card Type ?
    card_type = models.CharField(choices=CARD_TYPE, max_length=1)
    card_id = models.CharField(max_length=16, validators=[
        MinLengthValidator(16), only_int], blank=True, help_text='16碼')
    due_date = models.CharField(max_length=4, validators=[
        MinLengthValidator(4), only_int], blank=True)
    valid_number = models.CharField(max_length=3, validators=[
        MinLengthValidator(3), only_int], blank=True)

    def __str__(self):
        return str(self.id)

# define Member


class Member(models.Model):
    SEX = (('0', '女性'), ('1', '男性'), ('2', '不選擇'))
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #member_name = models.CharField(blank=False, max_length=20)
    member_sex = models.CharField(choices=SEX, max_length=1, help_text='輸入性別')
    member_addr = models.CharField(blank=False, max_length=50)
    #member_email = models.EmailField(max_length=254)
    member_birth = models.DateField(blank=True)
    member_phone = models.CharField(blank=False, max_length=10)

    def __str__(self):
        return self.user.username

    # member_register_date = models.DateField(auto_now_add=timezone.now)
    # member_login = models.DateField(auto_now_add=timezone.now)  # 現在登入時間
    # member_pwd = models.CharField(max_length=20)
    # Password in django https://stackoverflow.com/questions/17523263/how-to-create-password-field-in-model-django


# user profile


# define Cart
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    member = models.ForeignKey(
        'Member', on_delete=models.CASCADE, default=None)
    # product = models.ManyToManyField(Product)
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, null=True)
    product_count = models.PositiveIntegerField()

    def get_product(self):
        return self.product

    def get_product_count(self):
        return self.product_count

# define Order
class Order(models.Model):
    ORDER_STATUS = (('0', '配送中'), ('1', '尚未配送'), ('2', '已送達'), ('3', '訂單不成立'))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    transaction = models.OneToOneField(
        Transaction, on_delete=models.SET_NULL, null=True)
    member = models.ForeignKey(
        'Member', on_delete=models.CASCADE, null=True)
    item = models.ManyToManyField(Item)
    order_datetime = models.DateTimeField(auto_now_add=timezone.now)
    rent_datetime = models.DateTimeField()
    order_status = models.CharField(
        choices=ORDER_STATUS, max_length=1, help_text='商品狀態', default='1')
    def get_available_member_id(self, order_id):
        return Order.objects.filter(id=order_id).values('member')

 
# define DueRecord
class ReturnRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    return_datetime = models.DateTimeField(auto_now=True)
    is_due = models.BooleanField(default=0)