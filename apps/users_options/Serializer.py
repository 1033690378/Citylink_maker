import re
from rest_framework import serializers
from users.models import UserProfile
from users_options.models import UserAddress


# 用户修改信息的序列化器
class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=30, allow_null=True, label="用户名")
    gender = serializers.CharField(max_length=6, label="性别")
    phone = serializers.CharField(max_length=11, required=True, label="手机号")
    email = serializers.EmailField(max_length=100, allow_null=True, label="邮箱")
    birthday = serializers.DateField(allow_null=True, label="出生年月")

    # 校验修改信息的正确格式
    def validate(self, attrs):
        # 邮箱的校验
        if attrs.get('email') is not None:
            if not re.match(r'[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}', attrs.get('email')):
                raise serializers.ValidationError('邮箱格式有误，请重新输入')
        return attrs

    # 修改用户信息
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username')
        instance.birthday = validated_data.get('birthday')
        instance.gender = validated_data.get('gender')
        instance.mobile = validated_data.get('phone')
        instance.email = validated_data.get('email')
        instance.save()
        return instance

    class Meta:
        model = UserProfile
        fields = ("username", "gender", "phone", "email", "birthday")


# 收货地址的序列化器
class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = UserAddress
        fields = '__all__'
