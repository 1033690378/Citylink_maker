from django.contrib import admin

from goods.models import GoodsCategory, Goods, GoodsImage, Banner


# 商品多级分类
@admin.register(GoodsCategory)
class GoodsCategoryAdmin(admin.ModelAdmin):
    list_per_page = 10  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['name', 'code', 'desc', 'category_type', 'parent_category_id', 'is_tab', 'add_time', ]


# 商品信息
@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_per_page = 20  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['name', 'click_num', 'sold_num', 'goods_num', 'market_price', 'shop_price', 'goods_brief',
                    'ship_free', 'is_new', 'is_hot', 'add_time', ]

    # 设置搜索框   需要填写搜索的字段
    search_fields = ['name']


# 商品详情轮播图
@admin.register(GoodsImage)
class BannerAdmin(admin.ModelAdmin):
    list_per_page = 15  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['goods', 'image', 'add_time', ]


# 首页轮播图信息
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_per_page = 10  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['image', 'index', 'add_time', ]
