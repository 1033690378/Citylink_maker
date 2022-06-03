import re
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


# 自定义一个认证成功所返回的数据
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user_id': user.id,
        'phone': user.phone,
    }


# 获取用户模型，django的认证用户模型
User = get_user_model()


def get_user_by_account(account):
    """
    添加通过手机号查询用户的方法
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):  # account 是手机号
            user = User.objects.get(phone=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """添加支持手机号登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)  # username 是手机号
        if user.check_password(password) and user:
            return user
