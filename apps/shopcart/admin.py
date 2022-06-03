from django.contrib import admin
from shopcart.models import ShoppingCart, OrderInfo, OrderGoods


# 购物车信息
@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_per_page = 15  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['goods', 'nums', 'name', 'add_time', ]

    # 设置搜索框   需要填写搜索的字段
    search_fields = ['goods']

    # 设置过滤器   需要填写过滤的字段
    list_filter = ['user']


# 订单信息
@admin.register(OrderInfo)
class OrderInfoAdmin(admin.ModelAdmin):
    list_per_page = 15  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['order_sn', 'pay_status', 'pay_type', 'trade_no', 'post_script', 'order_mount', 'pay_time',
                    'signer_name', 'signer_mobile', 'address', 'name', 'add_time', ]

    # 设置搜索框   需要填写搜索的字段
    search_fields = ['order_sn']

    # 设置过滤器   需要填写过滤的字段
    list_filter = ['user_id']


# 订单内的商品详情
@admin.register(OrderGoods)
class OrderGoodsAdmin(admin.ModelAdmin):
    list_per_page = 15  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['order', 'goods', 'goods_num', 'name', 'add_time', ]

    # 设置搜索框   需要填写搜索的字段
    search_fields = ['order']
