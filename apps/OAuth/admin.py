from django.contrib import admin
from OAuth.models import OAuthQQUser


# QQ登录用户数据
@admin.register(OAuthQQUser)
class OAuthQQUserAdmin(admin.ModelAdmin):
    list_per_page = 10  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['user', 'openid', 'add_time', ]
