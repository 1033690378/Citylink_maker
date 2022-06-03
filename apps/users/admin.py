from django.contrib import admin
from users.models import UserProfile
from users_options.models import UserAddress

admin.site.site_title = '城联创客'
admin.site.site_header = '城联创客'
admin.site.index_title = '城联创客'


# 用户个人信息
@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
    list_per_page = 5  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['username', 'birthday', 'gender', 'phone', 'email', 'last_login', ]

    # 设置搜索框   需要填写搜索的字段
    search_fields = ['phone']

    # 设置显示编辑 ，fieldsets 与 fields 只能二选一 不能一起用
    # fieldsets = (
    #     ('基础信息', {'fields': ['username', 'password', 'birthday', 'gender', 'phone', 'email', ]}),
    # )


# 收货地址
@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_per_page = 5  # 设置一页显示多少条数据 默认不写的话，是一页100条

    # 设置显示里面的列属性
    list_display = ['province', 'city', 'district', 'address', 'signer_name', 'signer_mobile', 'name', ]

    # 设置过滤器   需要填写过滤的字段
    list_filter = ['user']

    # 设置显示编辑 ，fieldsets 与 fields 只能二选一 不能一起用
    fieldsets = (
        ('基础信息', {'fields': ['province', 'city', 'district', 'address', 'signer_name', 'signer_mobile', ]}),
    )
