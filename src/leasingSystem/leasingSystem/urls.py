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
from leasing.views import RegisterAPI
from django.urls import path
from knox import views as knox_views
from leasing.views import LoginAPI
from django.urls import path


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
router.register(r'duerecord', views.DuerecordViewSet)

urlpatterns = [
    path('', home_page),
    # re_path(r'^admin?/'$) # 正規化
    path('admin/', admin.site.urls),
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    re_path(r'^api/', include(router.urls))
]
