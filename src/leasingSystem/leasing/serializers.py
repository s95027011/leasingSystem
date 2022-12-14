from rest_framework import serializers
from leasing.models import Type, Product, Item, Transaction, Member, Cart, Order, ReturnRecord, User
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'], validated_data['email'], validated_data['password'])

        return user


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class ReturnRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRecord
        fields = '__all__'
        
# class OrderViewSerializer(serializers.Serializer):
#     PRODUCT_SIZE = (
#         ('S', 'small'),
#         ('M', 'medium'),
#         ('L', 'large'),
#         ('XL', 'extra large'),
#     )

#     product_name = serializers.CharField(max_length=20)
#     product_size = serializers.CharField(
#         max_length = 2,
#         chooices=PRODUCT_SIZE,
#         default='m',
#         help_text='服裝尺碼'
#     )
    

#     class Meta:
#         model = Order
#         fields = ('product_name', 'product_size', 'product_price', 'product_image', 'rent_time', 'return_time', 'count')

