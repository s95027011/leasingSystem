"""leasingSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from .view import home_page  # view的class
from rest_framework.routers import DefaultRouter
from leasing import views
from leasing.views import RegisterAPI, LoginAPI, UserAPI
from knox import views as knox_views
from django.contrib import admin
from django.conf.urls.static import static  # 需要添加这句，包含静态资源之类的
from leasing import views
from . import settings


urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
]
router = DefaultRouter()
router.register(r'productType', views.TypeViewSet)
router.register(r'product', views.ProductViewSet)
router.register(r'item', views.ItemViewSet)
router.register(r'transaction', views.TransactionViewSet)
router.register(r'member', views.MemberViewSet)
router.register(r'cart', views.CartViewSet)
router.register(r'order', views.OrderViewSet)
router.register(r'returnRecord', views.ReturnRecordViewSet)

urlpatterns = [
    path('', home_page),
    # re_path(r'^admin?/'$) # 正規化
    path('admin/', admin.site.urls),
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/user/', UserAPI.as_view()),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api/', include(router.urls))
]
