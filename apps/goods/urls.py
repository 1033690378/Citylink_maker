from django.urls import re_path
from rest_framework.routers import DefaultRouter
from goods import views

urlpatterns = [
    # 商品详情页的路由
    re_path(r'^goods/(?P<pk>.*)/$', views.GoodsView.as_view()),
    # 首页热销商品的路由
    re_path(r'^hotgoods/$', views.HotGoodsView.as_view()),
    # 首页新品到货的的路由
    re_path(r'^newgoods/$', views.NewGoodsView.as_view()),
    # 搜索的路由
    re_path(r'^search(?P<pk>.*)/$', views.SearchGoodsView.as_view()),
]

# 视图用了ModelViewSet，必须要用这个DefaultRouter
# 第一次用router的话，要router = DefaultRouter()，这个只能实例化一次，否则会覆盖原有的实例化对象，之后要用的话要继承
router = DefaultRouter()
router.register('categories', views.GoodsCategoriesView, basename="categories")  # 商品分类的路由
router.register('banner', views.BannersView, basename="banner")  # 首页轮播图的路由
urlpatterns += router.urls
