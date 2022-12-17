from django.shortcuts import render, get_object_or_404
from django.http import Http404
from rest_framework.decorators import action
from rest_framework import viewsets, status, mixins, generics, permissions
from rest_framework.response import Response
from leasing.models import Type, Product, Item, Transaction, Member, Cart, Order, ReturnRecord
from leasing.serializers import TypeSerializer, ProductSerializer, ItemSerializer, TransactionSerializer,MemberSerializer, CartSerializer, OrderSerializer, ReturnRecordSerializer
from rest_framework import generics, permissions
from rest_framework import generics, permissions
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer
from django.contrib.auth import login
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from datetime import datetime, timedelta
import uuid
from itertools import chain
import json
import json

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

    @action(detail=False, methods=['post'])
    def create_order_by_cart(self, request):
        '''
        param: 
            transaction,
            member
            rent_datetime,
            order_status,

            從購物車去抓item，不用cart_id
        '''
        member_id = request.data['member']
        cart_product_list = Cart.objects.filter(member_id=member_id)
        
        invalid_product_list = []
        valid_item_id_list = []
        for cart in cart_product_list:
            product = cart.get_product()
            product_count = cart.get_product_count()
            available_product_count = Item().get_available_product_count(product_id=product.id)
            if product_count > available_product_count:
                invalid_product_list.append(product)
            else: 
                item_list = Item.objects.filter(product_id=product.id)[:product_count]
                valid_item_id_list += [str(item.id) for item in item_list]
        
        # data =  {
        #             'member' : member_id,
        #             'transaction' : request.data['transaction'],
        #             'order_status' : request.data['order_status'],
        #             'rent_datetime' : request.data['rent_datetime'],
        #             'item' : valid_item_id_list,
        #         } 
        # data = json.dumps(data)

        order_serializer = OrderSerializer
        order_serializer.data['member'] = member_id
        order_serializer.data['transaction'] = request.data['transaction']
        order_serializer.data['order_status'] = request.data['order_status']
        order_serializer.data['rent_datatime'] = request.data['rent_datetime']
        order_serializer.data['item'] = valid_item_id_list
  
        print(order_serializer.data)
        # self.perform_create()
        return Response('test')


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
        item = request.data['item_id']
        order_id = request.data['order_id']
        # query_order = Order.objects.all().filter(order_id__in=order_id)
        query_order = Order.objects.all().filter(item_id__in=item)
        query_product = Product.objects.all().filter(item_id__in=item).only('product_name', 'product_size', 'product_price', 'product_image')
        query = chain(query_order, query_product)
        serializer = OrderSerializer(query, many=True)
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


class ReturnRecordViewSet(mixins.CreateModelMixin,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = ReturnRecord.objects.all()
    serializer_class = ReturnRecordSerializer
    def perform_create(self, serializer):
        is_due = serializer.validated_data['is_due']
    @action(detail=False, methods=['post'])
    def member_Return_record_by_manager(self, request):
        order= request.data['order']
        # member_id = Order().get_available_member_id(order_id=order)
        # query = ReturnRecord.objects.raw(
        # 'SELECT leasing_returnrecord.id,leasing_order.member_id,leasing_returnrecord.order_id,leasing_returnrecord.return_datetime,leasing_returnrecord.is_due FROM leasing_returnrecord JOIN leasing_order ON leasing_returnrecord.order_id=leasing_order.id and leasing_order.member_id =(SELECT leasing_order.member_id  FROM leasing_order where leasing_order.id=%s)'
        # , [order])
        query = ReturnRecord.objects.raw(
        'SELECT leasing_returnrecord.id,member_id,leasing_returnrecord.order_id,leasing_returnrecord.return_datetime,leasing_returnrecord.is_due FROM leasing_returnrecord JOIN leasing_order ON leasing_returnrecord.order_id=leasing_order.id '
        ,)
        serializer = ReturnRecordSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'])
    def member_Return_record_by_member(self, request):
        order = request.data['order']
        query = Order.objects.raw(

        )
        serializer = OrderSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'])
    def total_fine(self, request):
        pass
