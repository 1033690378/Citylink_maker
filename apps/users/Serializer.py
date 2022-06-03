import re
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import UserProfile


# 验证码的序列化器
class Sms_CodeSerializer(serializers.Serializer):
    # 手机号
    phone = serializers.CharField(label='手机号')

    # 处理手机号格式的异常
    def validate_mobile(self, value):
        # 数据库中是否存在该手机号
        if UserProfile.objects.filter(phone=value).count():
            raise serializers.ValidationError('该手机号已注册')
        # 手机号的格式检测
        if not re.match(r'^1[3-9]\d{9}', value):
            raise serializers.ValidationError('手机号不合法')

        return value


# 获取用户模型，django的认证用户模型
User = get_user_model()


# 用户注册的序列化器
class UserRegSerializer(serializers.ModelSerializer):
    # 手机号，required是否必填
    phone = serializers.CharField(label="手机号", help_text="手机号", required=True, allow_blank=False,
                                  validators=[UniqueValidator(queryset=User.objects.all(), message="手机号已存在")])
    # 用户名
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False)
    # 密码
    password = serializers.CharField(style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True)
    # 验证码
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")

    # 校验密码和验证码的格式和范围
    def validate(self, attrs):
        # print(attrs)  # 前端信息
        phone = attrs.get('phone')  # 获取手机号
        redis_conn = get_redis_connection('verify_codes')  # redis缓存
        try:
            result = redis_conn.get('sms_%s' % phone).decode()  # 验证码
        except AttributeError:
            # 验证码过期了，是500的报错，NoneType不能转码
            result = None
        # 检测验证码的长度
        if len(attrs.get('code')) != 4:
            raise serializers.ValidationError('验证码长度错误')
        # 当缓存中的验证码过期丢失
        if not result:
            raise serializers.ValidationError('验证码已过期')
        # 如果用户传过来的验证码与缓存中的验证码不符
        if attrs.get('code') != result:
            raise serializers.ValidationError('验证码错误，或验证码已过期')
        # 密码的长度校验 密码长度为 6-20之间
        if len(attrs.get('password')) < 6 or len(attrs.get('password')) > 20:
            raise serializers.ValidationError('密码长度不正确，应为6-20位')
        # 密码的格式校验 密码必须要数字与字母组成
        if not attrs.get('password').isalnum():
            raise serializers.ValidationError('密码应由字母与数字组成')
        # 密码范围校验
        if not re.match(r'[a-zA-Z]{1,19}\d+', attrs.get('password')):
            raise serializers.ValidationError('密码不正确')

        return attrs

    # 注册后创建用户
    def create(self, validated_data):
        del validated_data['code']
        user = User(**validated_data)
        # 对明文密码进行加密
        user.set_password(user.password)
        user.save()
        return user

    class Meta:
        model = User
        # 校验字段
        fields = ("phone", "password", "code", "username")


# 忘记密码的序列化器
class UserpwdSerializer(serializers.ModelSerializer):
    # 手机号，required是否必填
    phone = serializers.CharField(label="手机号", help_text="手机号", required=True, allow_blank=False)
    # 密码
    password = serializers.CharField(style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True)

    # 校验手机号和密码的格式和范围
    def validate(self, attrs):
        # print(attrs)  # 前端信息
        # 判断手机号是否存在与数据库中
        if not User.objects.filter(phone=attrs.get('phone')):
            raise serializers.ValidationError('该手机号不存在，请注册后重试')
        # 密码的长度校验 密码长度为 6-20之间
        if len(attrs.get('password')) < 6 or len(attrs.get('password')) > 20:
            raise serializers.ValidationError('密码长度不正确，应为6-20位')
        # 密码的格式校验 密码必须要数字与字母组成
        if not attrs.get('password').isalnum():
            raise serializers.ValidationError('密码应由字母与数字组成')
        # 密码范围校验
        if not re.match(r'[a-zA-Z]{1,19}\d+', attrs.get('password')):
            raise serializers.ValidationError('密码不正确')
        return attrs

    class Meta:
        model = User
        # 校验字段
        fields = ("phone", "password")


# 手机号验证码登录的序列化器
class LoginSerializer(serializers.ModelSerializer):
    # 手机号，required是否必填
    phone = serializers.CharField(label="手机号", help_text="手机号", required=True, allow_blank=False)
    # 验证码
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")

    # 校验手机号和密码的格式和范围
    def validate(self, attrs):
        # print(attrs)  # 前端信息
        # 判断手机号是否存在与数据库中
        if not User.objects.filter(phone=attrs.get('phone')):
            raise serializers.ValidationError('该手机号不存在，请注册后重试')
        if not re.match(r'^1[3-9]\d{9}', attrs.get('phone')):
            raise serializers.ValidationError('手机号不合法，请重新输入')

        redis_conn = get_redis_connection('verify_codes')  # redis缓存
        try:
            result = redis_conn.get('sms_%s' % attrs.get('phone')).decode()  # 验证码
        except AttributeError:
            # 验证码过期了，是500的报错，NoneType不能转码
            result = None
        # 检测验证码的长度
        if len(attrs.get('code')) != 4:
            raise serializers.ValidationError('验证码长度错误')
        # 当缓存中的验证码过期丢失
        if not result:
            raise serializers.ValidationError('验证码已过期')
        return attrs

    class Meta:
        model = User
        fields = ("phone", "code")
