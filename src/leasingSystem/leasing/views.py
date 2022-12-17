from django.shortcuts import render, get_object_or_404
from django.http import Http404
from rest_framework.decorators import action
from rest_framework import viewsets, status, mixins, generics, permissions
from rest_framework.response import Response
from leasing.models import Type, Product, Item, Transaction, Member, Cart, Order, ReturnRecord
from leasing.serializers import TypeSerializer, ProductSerializer, ItemSerializer, TransactionSerializer, MemberSerializer, CartSerializer, OrderSerializer, ReturnRecordSerializer, OrderByProductSerializer
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer
from django.contrib.auth import login
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from datetime import datetime, timedelta
import uuid
from itertools import chain
from django.db.models import Avg, Count, Min, Sum
# Create your views here.
################################################################
################################################################
# login api


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)

# register api


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
################################################################
################################################################


class TypeViewSet(viewsets.ModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAuthenticated, ]


class ItemViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # permission_classes = [permissions.IsAuthenticated, ]
    @action(detail=False)
    def list_by_product_status(self, request):
        product_id = request.query_params.get('product_id', None)
        available = request.query_params.get('available', None)
        query = ''
        if available == 'True':  # 上架
            query = Item.objects.all().filter(
                product_id__in=product_id).filter(item_status__in='0')
        elif available == 'False':  # 以出租
            query = Item.objects.all().filter(
                product_id__in=product_id).filter(item_status__in='1')
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


class TransactionViewSet(mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class CartViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        input_count = serializer.validated_data['product_count']
        item_count = Item().get_available_product_count(product_id=product)

        if input_count < 1 or input_count > item_count:
            raise Http404
        return super().perform_create(serializer)

    @action(detail=False, methods=['post'])
    def list_cart_by_member(self, request):
        member_id = request.data['member_id']
        query = Cart.objects.all().filter(member_id__in=member_id)
        serializer = CartSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        count = int(request.data['product_count'])
        product = request.data['product']
        data = {'product_count': count}
        avilable_count = Item().get_available_product_count(product_id=product)
        if count > 0 and count <= avilable_count:
            model = get_object_or_404(Cart, pk=pk)
            serializer = CartSerializer(model, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            # return a meaningful error response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise Http404

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        member_id = request.data['member_id']
        Cart.objects.all().filter(member_id__in=member_id).delete()
        return Response('sucess', status=status.HTTP_200_OK)


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):        
        item_list = serializer.validated_data['item']
        rent_datetime = serializer.validated_data['rent_datetime']

        valid_item_list = []
        invalid_item_list = []

        # 檢查item狀態，如果可以出租，更改其狀態
        for item in item_list:
            if item.get_item_status() != '0':
                invalid_item_list.append(item)
            else:
                valid_item_list.append(item)
        
        print(invalid_item_list)
        if invalid_item_list:
            message = ''
            for invalid_item in invalid_item_list:
                message += invalid_item.__str__()  + '\n'
            message += '沒庫存' 
            return Response(message)       
        for valid_item in valid_item_list:
            valid_item.set_item_stauts(1)
        now = datetime.now().replace(second=0, microsecond=0)
        rent_datetime_notz = rent_datetime.replace(tzinfo=None)
        if rent_datetime_notz < now and rent_datetime_notz > (now + timedelta(days=13)):
            return Response('出租時間不符合規定')
        return super().perform_create(serializer)


    def patch(self, request, pk=None):
        model = get_object_or_404(Order, pk=pk)
        order_status = request.data['order_status']
        data = {'order_stauts': order_status}
        serializer = OrderSerializer(model, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # return a meaningful error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def list_order_by_member(self, request):
        member = request.data['member']
        query = Order.objects.all().filter(member_id__in=member)
        serializer = OrderSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def list_order_overview(self, request):
        item_id = request.data['item']
        # order_id = request.data['id']
        # product_id = request.data['product_id']
        query_product = Product.objects.all().only('product_id','product_name', 'product_size', 'product_price', 'product_image')
        # query_order = Order.objects.filter(item__in=query_item).select_related('Item').values_list('item','rent_datetime', 'order_datetime')
        # id, item, member, member_id, order_datetime, order_status, rent_datetime, returnrecord, transaction, transaction_id
        query_order = Order.objects.all().select_related('Item').values_list('item', 'order_datetime', 'rent_datetime')
        # query_order = Order.objects.all().filter(order_id__in=order_id)
        # query_order = Order.objects.all().filter(item_id__in=item)
        # print('query_order')
        # print(query_order.query)
        query_item = Item.objects.filter(id=item_id).values_list('id', 'product_id')
        query_product = Product.objects.filter(id__in=Item.objects.filter(id=item_id).values_list('product_id')).values_list('id', 'product_name', 'product_size', 'product_price', 'product_image')
        query_item_product = chain(query_item, query_product)
        # print('query_product')
        # print(query_product.query)
        # count_product = Item.objects.annotate(count=Count('product_id')).filter(item__in=query_item)
        query = chain(query_order, query_item_product)
        serializer = OrderByProductSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # serializer = OrderProductSerializer(query, many=True)

        # query = Order.objects.raw(
        #     '''
        #     select product_name, product_size, product_price, product_image, rent_time, return_time, SUM(product_id) as count
        #     from leasing_order as o
        #     left join leasing_order_item as order_item
        #         on o.id = order_item.order_id
        #     left join leasing_item as item
        #         on order_item.item_id = item.id
        #     left join leasing_product as product
        #         on item.product_id = product.id
        #     where o.id = %
        #     group by product_name, product_size, product_price, product_image, rent_time, return_time;
        # ''', [order_id])

        # pass


class ReturnRecordViewSet(viewsets.ModelViewSet):
    queryset = ReturnRecord.objects.all()
    serializer_class = ReturnRecordSerializer
