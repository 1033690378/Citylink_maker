from django.db import models
from users.models import UserProfile


# QQ登录用户数据
class OAuthQQUser(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name
