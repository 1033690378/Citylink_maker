import json
import logging
from alipay import AliPay, AliPayConfig
from datetime import datetime
from django.shortcuts import redirect
from rest_framework.generics import ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from Citylink_maker.settings import app_private_key_string, alipay_public_key_string, ALIPAY_APPID
from shopcart.Serializer import ShopCartDetailSerializer, ShopCartSerializer, OrderGoodsSerializer, \
    OrderCreateSerializer, OrderDetailSerializer
from shopcart.models import ShoppingCart, OrderInfo, OrderGoods

# 设置日志
logger = logging.getLogger('django')


# 购物车的视图
class ShopCartView(ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShopCartDetailSerializer

    # 在修改之前先做一下用户的认证
    permission_classes = [IsAuthenticated]
    # 传一下用户的token
    authentication_classes = [JSONWebTokenAuthentication]

    # 如果视图是ModelViewSet并且要用到前端传递的pk值的话，就要设置lookup_field，传递前端给的pk值
    lookup_field = 'goods_id'

    def get_serializer_class(self):
        # 判断是否为查询
        if self.action == "list":
            # 购物车信息查看的序列化器
            return ShopCartDetailSerializer
        else:
            # 购物车信息操作的序列化器
            return ShopCartSerializer

    # 筛选当前的用户的购物车信息
    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


# 清空购物车的视图
class ShopCartClear(APIView):
    def post(self, request):
        user = request.user
        cart = ShoppingCart.objects.filter(user=user).delete()
        return Response({"message": "该用户购物车清空成功"}, status=201)


# 订单的视图 
class OrderView(ModelViewSet):
    serializer_class = None
    # 在修改之前先做一下用户的认证
    permission_classes = [IsAuthenticated]
    # 传一下用户的token
    authentication_classes = [JSONWebTokenAuthentication]

    # 筛选当前的用户的订单信息
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    # 订单的判定
    def get_serializer_class(self):
        # 当订单已存在，你使用的序列化器
        # retrieve是查看单个数据，list是查看多个数据的
        if self.action == 'retrieve':
            return OrderGoodsSerializer
        # 当订单不存在，你使用的序列化器
        return OrderCreateSerializer

    # 创建订单后，对比订单信息中的商品，删除购物车中订单商品的数据
    def perform_create(self, serializer):
        # 保存并获取订单的模型对象
        order = serializer.save()
        # print(2, order)

        # 获取订单中的商品信息
        products = self.request.data['products']
        # 因为前端传的是json格式的，要转换一下
        products = json.loads(products)
        # print(1, products)
        # print(2, type(products))

        # 遍历订单的商品信息
        for i in range(len(products)):
            # 获取在购物车中的订单信息中的商品的商品信息
            shoppingcart = ShoppingCart.objects.filter(user=self.request.user, goods=products[i]['goods'])
            # print(1, shoppingcart)
            # 判定订单中的商品是否满足库存数，获取的信息要遍历才能用
            for shopcart in shoppingcart:
                # 商品订单模型对象
                order_goods = OrderGoods()
                # 把商品从订单信息中传入订单中
                order_goods.goods = shopcart.goods
                # 把商品数量从订单信息中传入订单中
                order_goods.goods_num = products[i]['nums']
                # 把模型对象里的的数据保存到订单中
                order_goods.order = order

                # 创建订单支付之后，
                # 库存数量 = 库存数量 - 购物车中的商品数量
                # shopcart.goods.goods_num -= shopcart.nums

                # 商品销量 = 商品销量 + 订单中的商品数量
                shopcart.goods.sold_num += products[i]['nums']
                # 商品数据保存
                shopcart.goods.save()
                # 订单商品详情保存
                order_goods.save()
                # 删除该商品在购物车的信息
                shopcart.delete()
        return order


# 支付完成后回调访问的视图
class AlipayReturnView(APIView):
    # 处理支付宝的返回结果，验证支付是否成功，如果成功就修改订单的支付状态
    def get(self, request):
        processed_dect = {}
        # 遍历alipay_url中返回的数据
        for key, value in request.GET.items():
            processed_dect[key] = value

        # print(processed_dect)
        # 取出密钥，在之后进行交易号验证的时候使用，如果没有就给None
        sign = processed_dect.pop("sign", None)

        alipay = AliPay(
            appid=ALIPAY_APPID,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type='RSA2',  # 指定加密方式，一般为RSA2或者RSA
            # 请求等待15秒，如果超时返回错误，可选项。
            config=AliPayConfig(timeout=15),
        )

        # 验证订单是否支付成功，verify函数中传入的是订单的信息和密钥
        # 如果支付成功，verify_result值为True
        verify_result = alipay.verify(processed_dect, sign)

        if verify_result:
            # 支付成功，获取订单信息并修改
            order_sn = processed_dect.get('out_trade_no', None)  # 获取订单编号
            trade_no = processed_dect.get('trade_no', None)  # 交易号
            # print(order_sn)
            # print(trade_no)
            # 获取商品订单的对象
            existed_order = OrderInfo.objects.filter(order_sn=order_sn).first()
            # print(existed_order)

            '''修改订单数据'''
            # 订单编号
            existed_order.trade_no = trade_no
            # 订单状态，支付成功后改成待收货
            existed_order.pay_status = 'Pending_Receipt'
            # 订单时间
            existed_order.pay_time = datetime.now()
            existed_order.save()
            # 重定向到首页
            # response = redirect('http://127.0.0.1')
            # response = redirect('http://1.14.136.68')
            response = redirect('http://www.legendweb.top')
            return response
        else:
            # 支付失败，获取订单信息并修改
            order_sn = processed_dect.get('out_trade_no', None)  # 获取订单编号
            trade_no = processed_dect.get('trade_no', None)  # 交易号
            # 获取商品订单的对象
            existed_order = OrderInfo.objects.filter(order_sn=order_sn).first()

            '''修改订单数据'''
            # 订单编号
            existed_order.trade_on = trade_no
            # 订单状态，支付失败后改成交易关闭
            existed_order.pay_status = 'Trading_Closed'
            # 订单时间
            existed_order.pay_time = datetime.now()
            existed_order.save()
            # 重定向到首页
            # response = redirect('http://127.0.0.1')
            # response = redirect('http://1.14.136.68')
            response = redirect('http://www.legendweb.top')
            return response


# 我的订单的视图
class OrderDetailView(ListAPIView):
    serializer_class = OrderDetailSerializer
    # 在修改之前先做一下用户的认证
    permission_classes = [IsAuthenticated]
    # 传一下用户的token
    authentication_classes = [JSONWebTokenAuthentication]

    # 筛选当前的用户的订单信息
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)


# 订单信息详情和订单状态修改的路由
class OrderInfoDetailView(ListAPIView, UpdateAPIView, DestroyAPIView):
    serializer_class = OrderDetailSerializer
    # 在修改之前先做一下用户的认证
    permission_classes = [IsAuthenticated]
    # 传一下用户的token
    authentication_classes = [JSONWebTokenAuthentication]

    # 筛选当前的用户的订单信息
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    # 重写list方法，通过order_sn值来过滤要获取订单信息
    def list(self, request, *args, **kwargs):
        # 获取要筛选的order_sn
        order_sn = kwargs.get('pk')
        # 通过order_sn过滤要获取的订单信息
        response = self.get_queryset().filter(order_sn=order_sn).first()
        serializer = self.get_serializer(response)
        return Response(serializer.data, status=201)

    # 重写update方法，通过order_sn值来过滤要修改的订单信息
    def update(self, request, *args, **kwargs):
        # 获取要筛选的order_sn
        order_sn = kwargs.get('pk')
        # 通过order_sn过滤要修改的订单信息
        response = self.get_queryset().filter(order_sn=order_sn).first()
        # print(response)
        # 订单状态，修改成已完成
        response.pay_status = 'Completed'
        # print(response.pay_status)
        # 保存订单状态
        response.save()
        return Response({"message": "已确认收货"}, status=201)

    # 重写 DestroyAPIView 类中的 destroy方法
    def destroy(self, request, *args, **kwargs):
        # 获取要筛选的order_sn
        order_sn = kwargs.get('pk')
        # 通过order_sn过滤要删除的订单信息，并执行删除操作
        obj = self.get_queryset().filter(order_sn=order_sn).delete()
        # 删除成功后给前端返回信息
        return Response({"messages": "订单删除成功"}, status=201)
