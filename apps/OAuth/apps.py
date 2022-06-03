from django.apps import AppConfig


class OauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'OAuth'
    verbose_name = '第三方登录'