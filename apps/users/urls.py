from django.urls import path
from apps.users import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # 验证码的路由  => 随机生成验证码，在使用Ucloud发送
    path('code/', views.SmscodeView.as_view()),
    # 注册的路由
    path('register/', views.RegisterView.as_view()),
    # 手机号密码登录的路由
    path('login/', obtain_jwt_token),
    # 手机号验证码登录的路由
    path('login1/', views.LoginView.as_view()),
    # 找回密码的路由
    path('findPwd/', views.find_pwdView.as_view()),
]
