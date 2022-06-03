from django.urls import re_path
from users_options import views

urlpatterns = [
    # 用户个人信息路由 --> 获取跟修改
    re_path(r'^userinfo/$', views.UserInfoView.as_view()),
    # 用户收货地址路由 --> 获取
    re_path(r'^address/$', views.AddressView.as_view()),
    # 用户收货地址路由 --> 修改跟删除
    re_path(r'^address/(?P<pk>.*)/$', views.AddressView.as_view()),
]
