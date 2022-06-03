from django.db import models
from users.models import UserProfile


# 用户收货地址模型
class UserAddress(models.Model):
    # 用户的外键关系
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    # 收货地址的详细字段
    province = models.CharField(max_length=16, verbose_name='省份')
    city = models.CharField(max_length=16, verbose_name='城市')
    district = models.CharField(max_length=16, verbose_name='区域')
    address = models.CharField(max_length=64, verbose_name='详细地址')
    signer_name = models.CharField(max_length=20, default="", verbose_name="签收人")
    signer_mobile = models.CharField(max_length=11, default="", verbose_name="手机号")
    add_time = models.DateTimeField(auto_now_add=True, auto_created=True, verbose_name="添加时间")

    class Meta:
        db_table = 'user_address'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.address

    # 这是我写的显示列的自定义方法，用于在收货地址中显示所属用户的列
    def name(self):
        return self.user

    name.short_description = '对应用户'  # 显示列的标题
