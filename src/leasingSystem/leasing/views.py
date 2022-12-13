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
    def list_by_product_status(self, request):
        product_id = request.query_params.get('product_id', None)
        available = request.query_params.get('available', None)
        query = ''
        if available == 'True': # 上架
            query = Item.objects.all().filter(product_id__in=product_id).filter(item_status__in = '0')
        elif available == 'False': #以出租
            query = Item.objects.all().filter(product_id__in=product_id).filter(item_status__in = '1')
        serializer = ItemSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False)
    def list_item_by_product(self, request):
        product_id = request.query_params.get('product_id', None)
    
        query = Item.objects.all().filter(product_id__in=product_id)
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
                            mixins.UpdateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class CartViewSet(  mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def list(self, request):
        member_id = request.query_params.get('member_id', None)
        query = Cart.objects.all().filter(member_id__in = member_id)
        serializer = CartSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def update(self, request, pk=None):
        count = request.data['product_count']
        query = ''
        if count == 0:
            query = self.destroy(self, request, pk=pk)
        elif count > 0:
            model = get_object_or_404(Member, pk=pk)
            query = Member.objects.filter(pk=model.pk).update(request.data)
        serializer = MemberSerializer(query)
        if serializer.is_valid:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # return a meaningful error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods='post')
    def clear_cart(self, request):
        member_id = request.data['member_id']
        query = Cart.objects.all().filter(member_id__in = member_id).delete()
        serializer = CartSerializer(query)
        if serializer.is_valid:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # return a meaningful error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods="post")
    def list_order_by_member(self, request):
        member = request.data['member_id']
        query = Item.objects.all().filter(member_id__in = member)
        serializer = OrderSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DuerecordViewSet(viewsets.ModelViewSet):
    queryset = Duerecord.objects.all()
    serializer_class = DuerecordSerializer
