from django.urls import re_path
from goods.urls import router
from shopcart import views

urlpatterns = [
    # 清空购物车的路由
    re_path(r'^shopcarts/clear/$', views.ShopCartClear.as_view()),
    # 支付宝支付后返回的路由
    re_path(r'^alipay/retrun/$', views.AlipayReturnView.as_view()),
    # 我的订单的路由
    re_path(r'^ordersdetails/$', views.OrderDetailView.as_view()),
    # 订单信息详情和订单状态修改的路由
    re_path(r'^ordersdetails/(?P<pk>.*)/$', views.OrderInfoDetailView.as_view()),
]

# 多次使用router的话要继承第一次用的那个，不然会覆盖第一次的那个实例化对象
# 视图用了ModelViewSet，必须要用这个DefaultRouter
router.register('shopcarts', views.ShopCartView, basename='shopcarts')  # 购物车的路由
router.register('orders', views.OrderView, basename='orders')  # 订单信息的路由
urlpatterns += router.urls
