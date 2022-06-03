from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import models
from goods.models import Goods

# 获取用户模型
User = get_user_model()


# 购物车
class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品")
    nums = models.IntegerField(default=1, verbose_name="购买数量")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        db_table = 'shoppingcart'
        verbose_name = '购物车'
        verbose_name_plural = verbose_name
        # 多个字段作为一个联合唯一索引，可以从user和goods两个对象查询购书车的数据
        unique_together = ("user", "goods")

    def __str__(self):
        return "%s(%d)".format(self.goods.name, self.nums)

    # 这是我写的显示列的自定义方法，用于在购物车中显示所属用户的列
    def name(self):
        return self.user

    name.short_description = '对应用户'  # 显示列的标题


# 订单信息
class OrderInfo(models.Model):
    ORDER_STATUS = (
        ("Trade_Paying", "待支付"),
        ("Trading_Closed", "交易关闭"),
        ("Pending_Receipt", "待收货"),
        ("Completed", "已完成"),
    )
    PAY_TYPE = (
        ("Alipay", "支付宝"),
        ("Wechat", "微信"),
    )
    # 用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    # 订单号,unique唯一
    order_sn = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name="订单编号")
    # 微信支付可能会用到
    # nonce_str = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name="随机加密串")
    # 支付宝支付时的交易号与本系统进行关联
    trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name=u"交易号")
    # 以防用户支付到一半不支付了
    pay_status = models.CharField(choices=ORDER_STATUS, default="Trade_Paying", max_length=30, verbose_name="订单状态")
    # 订单的支付类型
    pay_type = models.CharField(choices=PAY_TYPE, default="Alipay", max_length=10, verbose_name="支付类型")
    post_script = models.CharField(max_length=200, verbose_name="订单留言")
    order_mount = models.FloatField(default=0.0, verbose_name="订单金额")
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")
    # 用户的基本信息
    address = models.CharField(max_length=100, default="", verbose_name="收货地址")
    signer_name = models.CharField(max_length=20, default="", verbose_name="签收人")
    signer_mobile = models.CharField(max_length=11, default="", verbose_name="联系电话")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'orderinfo'
        verbose_name = "订单信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_sn

    # 这是我写的显示列的自定义方法，用于在商品收藏中显示所属用户的列
    def name(self):
        return self.user

    name.short_description = '对应用户'  # 显示列的标题


# 订单内的商品详情
class OrderGoods(models.Model):
    # 一个订单对应多个商品，所以添加外键
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name="订单信息", related_name="goods")
    # 两个外键形成一张关联表
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品")
    goods_num = models.IntegerField(default=0, verbose_name="商品数量")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        db_table = 'ordergoods'
        verbose_name = "订单商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order.order_sn

    # 这是我写的显示列的自定义方法，用于在订单内的商品详情中显示所属用户的列
    def name(self):
        return self.order.user

    name.short_description = '对应用户'  # 显示列的标题
