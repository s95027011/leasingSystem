from rest_framework import serializers
from leasing.models import Type, Product, Item, Transaction, Member, Cart, Order, Duerecord

class TypeSerializer(serializers.Serializer):
    class Meta:
        model = Type
        fields = '__all__'

class ProductSerializer(serializers.Serializer):
    class Meta:
        model = Product
        fields = '__all__'

class ItemSerializer(serializers.Serializer):
    class Meta:
        model = Item
        fields = '__all__'

class TransactionSerializer(serializers.Serializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class MemberSerializer(serializers.Serializer):
    class Meta:
        model = Member
        fields = '__all__'

class CartSerializer(serializers.Serializer):
    class Meta:
        model = Cart
        fields = '__all__'

class OrderSerializer(serializers.Serializer):
    class Meta:
        model = Order
        fields = '__all__'

class DuerecordSerializer(serializers.Serializer):
    class Meta:
        model = Duerecord
        fields = '__all__'

# class leasingSerializer(serializers.ManyRelatedField):
#     class Type:
#         model = Type
#         fields = ('id', 'name')

#     class Product:
#         model = Product
#         fields = ('id', 'product_name', 'product_szie', 'product_type',
#                   'product_price', 'product_fine')

#     class Item:
#         model = Item
#         fields = ('id', 'product', 'item_status')

#     class Transaction:
#         model = Transaction
#         fields = ('id', 'payment', 'trans_time', 'bank_id',
#                   'card_type', 'card_id', 'dueD_date')

#     class Member:
#         model = Member
#         fields = ('id', 'member_sex', 'member_addr', 'member_birth')

#     class Cart:
#         model = Cart
#         fields = ('id', 'member', 'product', 'cart_count')

#     class Order:
#         model = Order
#         fields = ('id', 'transaction', 'member', 'item', 'order_time',
#                   'rent_time', 'order_status', 'order_price', 'return_time')

#     class Duerecord:
#         model = Duerecord
#         fields = ('id', 'order', 'due_day')
