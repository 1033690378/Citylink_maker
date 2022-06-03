import json
import time
from random import Random
from alipay import AliPay, AliPayConfig
from django.db import transaction
from rest_framework import serializers
from Citylink_maker.settings import app_private_key_string, alipay_public_key_string, ALIPAY_APPID, ALIPAY_URL
from goods.Serializer import GoodsSerializer
from goods.models import Goods
from shopcart.models import ShoppingCart, OrderGoods, OrderInfo


# 购物车信息查看的序列化器
class ShopCartDetailSerializer(serializers.ModelSerializer):
    # 获取商品的序列化器
    goods = GoodsSerializer()

    class Meta:
        model = ShoppingCart
        fields = '__all__'


# 购物车信息操作的序列化器
class ShopCartSerializer(serializers.Serializer):
    # 外键，指定默认的用户字段
    # 用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # 数量，required必填
    nums = serializers.IntegerField(required=True, label='数量', min_value=1,
                                    error_messages={
                                        "min_value": "商品数量不能小于1",
                                        "required": "请选择购买数量",
                                    })
    # 商品信息，required必填
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())

    # 重写create方法，判断购物车是否已经有商品
    def create(self, validated_data):
        # 获取当前你的登录用户
        user = self.context["request"].user
        # 获取前端传递过来的商品数量
        nums = validated_data['nums']
        # 获取前端传递过来的商品id
        goods = validated_data["goods"]
        # 查询你的购物车中是否有该商品信息
        exist = ShoppingCart.objects.filter(user=user, goods=goods)
        # 判定你的购物车中是否有商品信息
        if exist:
            ins = exist.first()
            ins.nums += nums  # 加上购物车的数量
            ins.save()
        else:
            ins = ShoppingCart.objects.create(**validated_data)
        return ins

    # 重写update方法，只更新购物车商品数量
    def update(self, instance, validated_data):
        # print(instance)
        instance.nums = validated_data['nums']
        instance.save()
        return instance


# 用于订单已存在，且一个订单只存在一个商品的情况
class OrderGoodsOneSerializer(serializers.ModelSerializer):
    # 商品信息
    goods = GoodsSerializer()

    class Meta:
        model = OrderGoods
        fields = '__all__'


# 用于订单已存在，且一个订单对应多个商品
class OrderGoodsSerializer(serializers.ModelSerializer):
    # 强调 many=true 是一个订单中有多个商品
    goods = OrderGoodsOneSerializer(many=True)

    class Meta:
        model = OrderGoods
        fields = '__all__'


# 用于订单未存在，创建一个订单
class OrderCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    products = serializers.JSONField(label='商品信息', read_only=True)
    pay_status = serializers.CharField(label='订单状态', read_only=True)
    post_script = serializers.CharField(default="", label="订单留言", read_only=True)
    order_sn = serializers.CharField(label='订单编号', read_only=True)
    create_time = serializers.DateTimeField(label='创建时间', read_only=True)
    # 增加支付宝交易号的字段
    trade_no = serializers.CharField(label='交易号', read_only=True)
    # 增加支付宝请求接口，需要安装第三方包， 包名：python-alipay-sdk
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        # 支付宝支付前的配置，绑定支付宝开放平台-沙箱应用
        alipay = AliPay(
            # 网页&移动应用
            appid=ALIPAY_APPID,  # APPID
            app_private_key_string=app_private_key_string,  # 应用私钥
            alipay_public_key_string=alipay_public_key_string,  # 支付宝的公钥
            sign_type='RSA2',  # 指定加密方式，一般为RSA2或者RSA
            # 请求等待15秒，如果超时返回错误，可选项。
            config=AliPayConfig(timeout=15),
        )
        order_string = alipay.api_alipay_trade_wap_pay(
            out_trade_no=obj.order_sn,  # 订单编号
            total_amount=obj.order_mount,  # 订单金额
            subject='城联创客商城订单：%s' % obj.order_sn,  # 订单主题
            # return_url='http://127.0.0.1:8000/alipay/retrun/',  # 支付完成后返回的地址
            return_url='http://1.14.136.68:8000/alipay/retrun/',  # 支付完成后返回的地址
            notify_url='http://example.com/notify',  # 可选
        )
        alipay_url = ALIPAY_URL + '?' + order_string
        return alipay_url

    # 订单编号生成
    def create_order_sn(self):
        random_str = Random()
        order_sn = "{time_str}{user_id}{random_str}".format(
            time_str=time.strftime("%Y%m%d%H%M%S"),  # 当前时间
            user_id=self.context['request'].user.id,  # 获取用户的id
            random_str=random_str.randint(10, 99),  # 写2个随机数减少被破解的可能
        )
        return order_sn

    # 数据校验
    def validate(self, attrs):
        # 获取当前的请求用户
        user = self.context['request'].user
        # 获取订单中商品的信息
        products = self.context['request'].data['products']
        # 因为前端传的是json格式的，要转换一下
        products = json.loads(products)
        # print(1, products)
        # print(type(products))

        # 如果是直接在商品详情页点击购买的或者是在待支付购买的就要先把订单信息中的商品先添加到购物车
        shoppingcart = ShoppingCart.objects.filter(user=user, goods=products[0]['goods'])
        if not shoppingcart:
            for i in range(len(products)):
                # 购物车模型对象
                order_goods = ShoppingCart()
                # 把用户信息从订单信息中传入购物车中
                order_goods.user = user
                # 把商品从订单信息中传入购物车中，必须是要是实例化对象，不能是数值所以要用.first()
                order_goods.goods = Goods.objects.filter(id=products[i]['goods']).first()
                # 把商品数量从订单信息中传入购物车中
                order_goods.nums = products[i]['nums']
                # 保存购物车
                order_goods.save()

        # 判断修改结果
        result = False
        # 获取当前用户的购物车商品信息
        shoppingcart = user.shoppingcart_set.all()
        # print(shoppingcart)
        # 开始事务
        with transaction.atomic():
            # 事务的存档点
            save_id = transaction.savepoint()
            # 遍历订单的商品信息
            for i in range(len(products)):
                # 获取在购物车中的订单信息中的商品的商品信息
                shopcart = user.shoppingcart_set.filter(user=user, goods=products[i]['goods'])
                # 判定订单中的商品是否满足库存数，获取的信息要遍历才能用
                for obj in shopcart:
                    # 判定数据库中的库存数据，获取的信息要遍历才能用
                    for obj_goods in shoppingcart:
                        # 判断是否已修改
                        if result:
                            break
                        else:
                            # print(obj.goods, obj_goods.goods, obj_goods.goods.id)
                            # 判定是否是这个商品
                            if obj.goods == obj_goods.goods:
                                # print(obj.goods, obj_goods.goods)
                                # 把原来的库存数量先保存
                                origin_nums = obj_goods.goods.goods_num
                                # 新的库存数量 = 原来的库存数量 - 上一个购物车中的商品数量
                                new_nums = origin_nums - products[i]['nums']
                                if products[i]['nums'] > origin_nums:
                                    # 回滚数据
                                    transaction.savepoint_rollback(save_id)
                                    raise serializers.ValidationError('商品库存不足')

                                # 第一个用户库存数量足够，就修改原来的库存数量，变成新的库存数量
                                res = Goods.objects.filter(id=obj_goods.goods.id).update(goods_num=new_nums)
                                # 修改成功
                                result = True
                                # 如果事务失败了，返回0
                                if res == 0:
                                    break
            # 提交事务
            transaction.savepoint_commit(save_id)

        # 添加商品订单号
        attrs['order_sn'] = self.create_order_sn()
        # 添加订单留言信息
        attrs['post_script'] = self.context['request'].data['post_script']
        return attrs

    class Meta:
        model = OrderInfo
        fields = '__all__'


# 我的订单，订单信息详情和订单状态修改的序列化器
class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsOneSerializer(many=True)

    # 重写获取商品的信息
    def get_goods(self, request):
        return OrderGoods.objects.filter(user=request.user)

    class Meta:
        model = OrderInfo
        fields = '__all__'
