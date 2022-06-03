"""Citylink_maker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.views.static import serve
from Citylink_maker import settings

urlpatterns = [
    path('admin/', admin.site.urls),  # 后端管理页面
    path('', include('apps.users.urls')),  # 用户登录注册模块
    path('', include('apps.users_options.urls')),  # 用户个人信息模块
    path('', include('apps.OAuth.urls')),  # 第三方登录模块
    path('', include('apps.goods.urls')),  # 商品信息模块
    path('', include('apps.shopcart.urls')),  # 购物车订单模块

    re_path(r'^media(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  # 访问留言的图片
    re_path(r'^static(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),  # 访问管理界面的logo
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),  # 富文本编辑器路由
]
