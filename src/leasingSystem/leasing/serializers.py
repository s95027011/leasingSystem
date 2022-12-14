from rest_framework import serializers
from leasing.models import Type, Product, Item, Transaction, Member, Cart, Order, ReturnRecord, User
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password],
                                     style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={
                                      'input_type': 'password'})
    email = serializers.EmailField(write_only=True, required=True)
    sex = serializers.CharField(max_length=1)
    addr = serializers.CharField(max_length=100)
    birth = serializers.DateField()
    phone = serializers.CharField(min_length=8, max_length=10, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password',
                  'password2', 'sex', 'addr', 'birth', 'phone')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        userprofile = Member.objects.create(
            user=user,
            member_sex=validated_data['sex'],
            member_addr=validated_data['addr'],
            member_birth=validated_data['birth'],
            member_phone=validated_data['phone'],
        )

        user.set_password(validated_data['password'])
        user.save()

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
    user = UserSerializer()  # 唯讀

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
