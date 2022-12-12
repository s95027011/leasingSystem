from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import action
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from leasing.models import Type, Product, Item, Transaction, Member, Cart, Order, Duerecord
from leasing.serializers import TypeSerializer, ProductSerializer, ItemSerializer, TransactionSerializer, MemberSerializer, CartSerializer, OrderSerializer, DuerecordSerializer

# Create your views here.
class TypeViewSet(viewsets.ModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ItemViewSet(  mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    
    @action(detail=False)
    def product_status(self, request):
        product_id = request.query_params.get('product_id', None)
        available = request.query_params.get('available', None)
        query = ''
        if available == 'True': # 上架
            query = Item.objects.raw('SELECT * FROM leasing_item WHERE product_id = %s AND item_status = 0', [product_id])
        elif available == 'False': #以出租
            query = Item.objects.raw('SELECT * FROM leasing_item WHERE product_id = %s AND item_status = 1', [product_id])
        serializer = ItemSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False)
    def list_item_by_product(self, request):
        product_id = request.query_params.get('product_id', None)
    
        query = Item.objects.raw('SELECT * FROM leasing_item WHERE product_id = %s', [product_id])
        serializer = ItemSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 僅能更新商品狀態
    def patch(self, request, pk=None):
        model = get_object_or_404(Item, pk=pk)
        data = {'item_status': request.data['item_status']}
        serializer = ItemSerializer(model, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # return a meaningful error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransactionViewSet(   mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    @action(detail=True, methods="POST")
    def change_transaction(self, request):
        
        pass

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods="POST")
    def list_order_by_member(self, request):
        member = request.data['member_id']
        query = Item.objects.raw("SELECT * FROM leasing_order WHERE member_id = %s", [member])
        serializer = OrderSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DuerecordViewSet(viewsets.ModelViewSet):
    queryset = Duerecord.objects.all()
    serializer_class = DuerecordSerializer
