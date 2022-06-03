from django.urls import path
from OAuth import views

urlpatterns = [
    # 提供QQ登录扫码页面的路由
    path('qq/login/', views.QQAuthURLView.as_view()),
    # QQ登录回调的路由
    path('qq/qqLoginCallback', views.QQAuthUserView.as_view()),
]
