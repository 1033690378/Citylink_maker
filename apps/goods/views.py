import logging
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from goods.Serializer import GoodsCategorySerializer, GoodsSerializer, HotGoodsSerializer, NewGoodsSerializer, \
    BannerSerializer
from goods.models import GoodsCategory, Goods, Banner

# 设置日志
logger = logging.getLogger('django')


# 商品详情页的视图
class GoodsView(ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer

    # 重写list方法
    def list(self, request, *args, **kwargs):
        # 获取商品的id
        pk = kwargs.get('pk')
        # 用商品id过滤所需要的商品的信息
        goods = self.get_queryset().filter(id=int(pk)).first()
        serializer = self.get_serializer(goods)
        response = serializer.data
        return Response(response)


# 商品分类视图
class GoodsCategoriesView(ModelViewSet):
    queryset = GoodsCategory.objects.all()
    serializer_class = GoodsCategorySerializer


# 热销商品的视图
class HotGoodsView(ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = HotGoodsSerializer

    # 重写list方法
    def list(self, request, *args, **kwargs):
        # 通过是否热销过滤所需要的商品的信息
        queryset = self.queryset.filter(is_hot=True).all()
        # print(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=201)


# 商品新品到货的视图
class NewGoodsView(ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = NewGoodsSerializer

    # 重写list方法
    def list(self, request, *args, **kwargs):
        # 通过是否新品过滤所需要的商品的信息
        queryset = self.queryset.filter(is_new=True).all()
        # print(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=201)


# 商品轮播图
class BannersView(ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer


# 分页函数
class GoodsPagination(PageNumberPagination):
    # 表示每页多少条数据，前端没有传入page_num，则默认显示此参数
    page_size = 5
    # 前端传入每页显示条数，向后台要多少条，分页数参数名
    page_size_query_param = 'page_size'
    # 定制多少页的参数，前端传入第几页
    page_query_param = "page"
    # 最大分为多少页，此处为100页，后端控制每页显示最大记录数
    max_page_size = 100


# 商品搜索视图
class SearchGoodsView(ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    # 数据分页
    pagination_class = GoodsPagination

    # 设置过滤器，用于过滤用户需要的数据信息
    # 需要安装django-filter包，还需要在子应用中注册一下 注册名称：django_filters
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # 设置过滤字段，商品名称，商品简单描述，商品内容
    search_fields = ('name', 'goods_brief', 'goods_desc')
