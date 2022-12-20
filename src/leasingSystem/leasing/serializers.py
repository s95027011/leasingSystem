from rest_framework import serializers
from leasing.models import Type, Product, Item, Transaction, Member, Cart, Order, ReturnRecord, User, File
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator


def only_int(value):
    if not value.isdigit():
        raise ValidationError('只能輸入數字')


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
    phone = serializers.CharField(
        validators=[
            MinLengthValidator(3), only_int], max_length=10, write_only=True)

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
            member_name=validated_data['username'],
            member_sex=validated_data['sex'],
            member_addr=validated_data['addr'],
            member_birth=validated_data['birth'],
            member_phone=validated_data['phone'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect Credentials Passed.')


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
    user = UserSerializer()

    class Meta:
        model = Member
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    # product = ProductSerializer(read_only=True)  # 唯讀
    # product.field_name = ['product_name', 'product_size', 'product_price', 'product_image']
    class Meta:
        model = Order
        fields = '__all__'


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # 唯讀

    class Meta:
        model = Order
        fields = ['id', 'product']


class ReturnRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRecord
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('file', 'remark', 'timestamp')
