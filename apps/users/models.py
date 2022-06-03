from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    GENDER_CHOICES = (
        ("male", u"男"),
        ("female", u"女")
    )
    # 用户名字段，blank=True，设置该字段可以不填，null=True，设置字段内容为空字符串
    username = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    # 出生日期字段，非必填，字段内容为空字符串
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    # 性别字段，非必填，默认为女，用户可以自行选择
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default="male", verbose_name="性别")
    # 手机号字段，非必填，默认为空字符串
    phone = models.CharField(null=True, blank=True, unique=True, max_length=11, verbose_name="手机号")
    # 邮箱字段，非必填，默认为空字符串
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


# 验证码的模型
class SmsModel(models.Model):
    phone = models.CharField(max_length=11, verbose_name='手机号')
    code = models.CharField(max_length=4, verbose_name='验证码')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'user_VerifyCode'
        ordering = ['-add_time']  # 进行倒计时
        verbose_name = "验证码"
        verbose_name_plural = verbose_name

    # 这是我写的显示列的自定义方法，用于在验证码中显示对应发送的手机号
    def phone_name(self):
        return self.phone

    phone_name.short_description = '对应手机号'  # 显示列的标题


# token的模型
class UserToken(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    token = models.CharField(max_length=255, verbose_name='用户令牌')

    class Meta:
        db_table = 'user_token'
        verbose_name = "Token"
        verbose_name_plural = verbose_name

    # 这是我写的显示列的自定义方法，用于在token中显示所属用户的名字
    def name(self):
        return self.user.username

    name.short_description = '对应用户名'  # 显示列的标题
