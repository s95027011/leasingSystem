from rest_framework.views import APIView
from .serializers import FileSerializer
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.models import Sum, F
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework import viewsets, status, mixins, generics, permissions
from rest_framework.response import Response
from leasing.models import Type, Product, Item, Transaction, Member, Cart, Order, ReturnRecord
from leasing.serializers import TypeSerializer, ProductSerializer, ItemSerializer, TransactionSerializer, MemberSerializer, CartSerializer, OrderSerializer, ReturnRecordSerializer, OrderProductSerializer
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from django.contrib.auth import login
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authentication import BasicAuthentication
from knox.views import LoginView as KnoxLoginView
from datetime import date, timedelta, datetime
from itertools import chain
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.serializers.json import DjangoJSONEncoder
import json
from rest_framework import generics
# Create your views here.
################################################################
################################################################
# login api


class LoginAPI(KnoxLoginView):
    permission_classes = [permissions.AllowAny, ]

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


# class SignUpAPI(generics.GenericAPIView):
#     serializer_class = RegisterSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         token = AuthToken.objects.create(user)
#         return Response({
#             "users": UserSerializer(user, context=self.get_serializer_context()).data,
#             "token": token[1]
#         })


# class SignInAPI(generics.GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data
#         return Response({
#             "user": UserSerializer(user, context=self.get_serializer_context()).data,
#             "token": AuthToken.objects.create(user)[1]
#         })


# class MainUser(generics.RetrieveAPIView):
#     permission_classes = [
#         permissions.IsAuthenticated
#     ]
#     serializer_class = UserSerializer

#     def get_object(self):
#         return self.request.user


class TypeViewSet(viewsets.ModelViewSet):
    #permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    def get_permissions(self):
        if self.action in ('create',):
            self.permission_classes = [IsAdminUser]
        return [permission() for permission in self.permission_classes]
    queryset = Type.objects.all()
    serializer_class = TypeSerializer

    @permission_classes((IsAdminUser))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
# 權限OK


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ('create',):
            self.permission_classes = [IsAdminUser]
        return [permission() for permission in self.permission_classes]
# Admin can create product

    @permission_classes((IsAdminUser))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
# Admin can update product

    @action(detail=False)
    def query_product(self, request):
        parm = request.query_params.get('query', None)
        query = Product.objects.filter(product_name__contains=parm)
        serializer = ProductSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        elif available == 'False':  # 已出租
            query = Item.objects.all().filter(
                product_id__in=product_id).filter(item_status__in='1')
        serializer = ItemSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False)
    def list_item_by_product(self, request):
        product_id = request.query_params.get('product_id', None)

        query = Item.objects.all().filter(product_id=product_id)
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

    def get_permissions(self):
        if self.action in ('list',):
            self.permission_classes = [IsAdminUser]
        return [permission() for permission in self.permission_classes]
# Admin can view member list

    @permission_classes((IsAdminUser))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class GetMemberView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = MemberSerializer

    def get_queryset(self):
        name = self.request.query_params.get('member_name')
        queryset = Member.objects.filter(member_name__icontains=name)
        return queryset


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
        member_id = request.data['member']
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
        print(type(request))
        member_id = request.data['member_id']
        # Cart.objects.all().filter(member_id__in=member_id).delete()
        Cart().clear_cart(member_id=member_id)
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
                item_list = Item.objects.filter(product_id=product.id).filter(
                    item_status='0')[:product_count]
                for item in item_list:
                    valid_item_id_list.append(str(item.id))
        data = {
            'rent_datetime': request.data['rent_datetime'],
            'order_status': '0',
            'transaction': request.data['transaction'],
            'member': member_id,
            'item': valid_item_id_list,
        }

        if invalid_product_list:
            message = ''
            for invalid_product in invalid_product_list:
                message += invalid_product.__str__() + '\n'
            message += '沒庫存'
            return Response(message)

        order_serializer = OrderSerializer(data=data)
        if order_serializer.is_valid():
            self.perform_create(order_serializer)
            Cart().clear_cart(member_id=member_id)
            return Response('sucess')
        return Response('fail')

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

        # 沒印出message !!
        if invalid_item_list:
            message = ''
            for invalid_item in invalid_item_list:
                message += invalid_item.__str__() + '\n'
            message += '沒庫存'
            return Response(message)

        for valid_item in valid_item_list:
            valid_item.set_item_status(1)

        now = date.today()
        if rent_datetime < now and rent_datetime > (now + timedelta(days=13)):
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
    def list_order_cost(self, request):
        cost = 0
        order_id = request.data['id']
        order_item = Order.objects.filter(id=order_id)
        query_order_item = order_item.values('rent_datetime','order_datetime')
        order_data={}
        query_product_item = Order.objects.filter(id=order_id).values('item__product__product_name','item__product__product_size','item__product__product_price','item__product__product_image')
        product_item=query_product_item.annotate(product_name=F('item__product__product_name'), product_size=F('item__product__product_size'), product_price=F('item__product__product_price'), product_image=F('item__product__product_image'))
        for num in range(len(product_item)):
            product_item_data = product_item[num]
            old_key = ['item__product__product_name','item__product__product_size','item__product__product_price','item__product__product_image']
            for key in old_key:
                product_item_data.pop(key, None)
            order_data=product_item_data
            order_data.update(query_order_item[num])
            cost += product_item_data['product_price']
            order_data.update({'all_cost':cost})
        return Response(order_data, status=status.HTTP_200_OK)
    # def list_order_cost(self, request):
    #     cost = 0
    #     order_id = request.data['id']
    #
    #     query = Order.objects.filter(id=order_id).values(
    #         'item__product__product_price')
    #     query = Order.objects.filter(id=order_id).values(
    #         'item__product__product_price')
    #     for cursor in query:
    #         cost += cursor['item__product__product_price']
    #     ###
    #
    #     query_order_item = Order.objects.all().filter(id=order_id).prefetch_related(
    #         'Item').values_list('item', 'rent_datetime', 'order_datetime')
    #     query_item_product = Item.objects.all().filter(id__in=query_order_item.only('item')).prefetch_related(
    #         'Prouct').values_list('id', 'product_id', 'product_name', 'product_size', 'product_price', 'product_image')
    #     # ###
    #
    #     # query_order_item = Order.objects.all().filter(id=order_id).prefetch_related('Item').values_list('item','rent_datetime','order_datetime')
    #     # query_item_product = Item.objects.all().filter(id__in = query_order_item.only('item')).prefetch_related('Prouct').values_list('id', 'product_id', 'product_name', 'product_size', 'product_price', 'product_image')
    #
    #     ###
    #     return Response(cost, status=status.HTTP_200_OK)
    #
    #     # ###
    #     return Response([{"cost": cost}], status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def list_order_by_member(self, request):
        member = request.data['member']
        query = Order.objects.all().filter(member_id=member)
        serializer = OrderSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['post'])
    # def list_order_overview(self, request):
    #     order_id = request.data['id']
    #     query = Order.objects.prefetch_related('item__product').filter(id=order_id).values('item__product_id')

    #     for curse in query:
    #         print('product_id : ', curse['item__product_id'])
    #         print(query.filter(product_id=curse['item__product_id']).count())
    #         print('-----------')
    #     print(query)
    #     # print(OrderProductSerializer(query, many=True).data)
    #     return Response('test')
        # item = request.data['item_id']
        # order_id = request.data['order_id']
        # # query_order = Order.objects.all().filter(order_id__in=order_id)
        # query_order = Order.objects.all().filter(item_id__in=item)
        # query_product = Product.objects.all().filter(item_id__in=item).only(
        #     'product_name', 'product_size', 'product_price', 'product_image')
        # query = chain(query_order, query_product)
        # serializer = OrderSerializer(query, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)

        # serializer = OrderProductSerializer(query, many=True)

        # query = Order.objects.raw(
        #     '''
        # select product_name, product_size, product_price, product_image, rent_time, return_time, SUM(product_id) as count
        # from leasing_order as o
        # left join leasing_order_item as order_item
        #     on o.id = order_item.order_id
        # left join leasing_item as item
        #     on order_item.item_id = item.id
        # left join leasing_product as product
        #     on item.product_id = product.id
        # where o.id = %
        # group by product_name, product_size, product_price, product_image, rent_time, return_time;
        # ''', [order_id])

        # pass


# class OrderProducrViewSet(viewsets.GenericViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderProductSerializer

#     @action(detail=False, methods=['post'])
#     def list_order_overview(self, request):
#         order_id = request.data['id']
#         print(order_id)
#         query = Order.objects.filter(id=order_id).values(
#                 'item__product',
#                 'item__product__product_name',
#                 'item__product__product_price',
#                 'item__product__product_image',
#                 'item__product__product_description')
#         print(query[0]['item__product'])
#         print(json.dumps(list(query), cls=DjangoJSONEncoder))
#         for cursor in query:
#             data = {
#                 "id": 2,
#                 "product_name": "DUCK CEO",
#                 "product_size": "m",
#                 "product_price": 12000,
#                 "product_fine": 1200,
#                 "product_image": "image/2.jpg",
#                 "product_description": "CEO",
#                 "product_type": [
#                     1
#                 ]
#             }
#             serializer = ProductSerializer(data=date, many=True)
#             if serializer.is_valid(raise_exception=True):
#                 return Response(serializer.data)

class ReturnRecordViewSet(mixins.CreateModelMixin,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):

    queryset = ReturnRecord.objects.all()
    serializer_class = ReturnRecordSerializer
    # def get_permissions(self):
    #     if self.action in ('perform_create',):
    #         self.permission_classes = [IsAdminUser]
    #     return [permission() for permission in self.permission_classes]

    # @permission_classes((IsAdminUser))
    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        order = str(order)
        renting_time = Order.objects.filter(
            id=order).values_list('rent_datetime', flat=True)
        renting_time = renting_time[0]
        now = date.today()
        now = datetime.strptime(str(now), '%Y-%m-%d')
        renting_time = datetime.strptime(str(renting_time), '%Y-%m-%d')
        delta = abs(now-renting_time)
        is_due = False
        if delta.days > 7:
            is_due = True
        serializer.validated_data['is_due'] = is_due
        item_id = Order.objects.filter(id=order).values_list(
            'item', flat=True)[0]  # Order裡面的item_id
        item = Item.objects.get(id=item_id)
        print(item.item_status)
        item.set_item_status(0)
        print(item.item_status)
        return super().perform_create(serializer)

    @action(detail=False, methods=['post', 'get'])
    def list_returnrecord(self, request):
        query = ReturnRecord.objects.filter(is_due=False)
        serializer = ReturnRecordSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def list_returnrecord_by_member_id(self, request):
        member_id = request.data['member']
        query = ReturnRecord.objects.select_related('order').filter(
            is_due=False).filter(order__member_id=member_id)
        # print(query.query)
        serializer = ReturnRecordSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post', 'get'])
    def list_duerecord(self, request):
        query = ReturnRecord.objects.filter(is_due=True)
        serializer = ReturnRecordSerializer(query, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def list_duerecord_by_member_id(self, request):
        member_id = request.data['member']
        query = ReturnRecord.objects.select_related('order').filter(
            is_due=True).filter(order__member_id=member_id)
        # print(query.query)
        serializer = ReturnRecordSerializer(query, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def get_total_penalty(self, request):  # 那筆訂單的罰款
        # request data 為 return_record 的 id (可視實際情況改)
        return_record_id = request.data['id']
        is_due = ReturnRecord.objects.filter(
            id=return_record_id).values_list('is_due', flat=True)[0]
        if not is_due:
            return Response("期限內歸還，沒有罰款")
        return_time = ReturnRecord.objects.filter(
            id=return_record_id).values_list('return_datetime', flat=True)[0]
        order_id = ReturnRecord.objects.filter(
            id=return_record_id).values_list('order', flat=True)[0]
        renting_time = Order.objects.filter(id=order_id).values_list(
            'rent_datetime', flat=True)[0]  # 訂單租賃時間
        expiration_date = renting_time + timedelta(days=7)  # 訂單到期時間(最晚歸還時間)
        return_time = datetime.strptime(str(return_time), '%Y-%m-%d')
        expiration_date = datetime.strptime(str(expiration_date), '%Y-%m-%d')
        delta = abs(return_time-expiration_date).days  # 總逾期天數
        itme_id = str(Order.objects.filter(id=order_id).values_list(
            'item', flat=True)[0])  # Order裡面的item_id
        product_id = str(Item.objects.filter(id=itme_id).values_list(
            'product', flat=True)[0])  # Item裡面的product_id
        product_penalty = str(Product.objects.filter(id=product_id).values_list(
            'product_fine', flat=True)[0])  # 抓product的罰款金額
        total_penalty = int(product_penalty)*delta  # 總罰款金額
        return Response([{"penalty": total_penalty}], status=status.HTTP_200_OK)

    def get_total_fine(self, request):
        pass


class FileView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
