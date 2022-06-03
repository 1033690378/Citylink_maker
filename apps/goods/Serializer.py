from rest_framework import serializers
from goods.models import GoodsCategory, Goods, GoodsImage, Banner


# 商品分类序列化器
class GoodsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'


# 商品图片序列化器
class GoodsImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = '__all__'


# 商品信息的序列化器
class GoodsSerializer(serializers.ModelSerializer):
    category = GoodsCategorySerializer()
    images = GoodsImagesSerializer(many=True)

    class Meta:
        model = Goods
        fields = "__all__"


# 热销商品的序列化器
class HotGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = "__all__"


# 商品新品到货的序列化器
class NewGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = "__all__"


# 轮播图的序列化器
class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"
