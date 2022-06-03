import random
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_jwt.settings import api_settings
from extar_apps.ucloud_sms_python import send_sms
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from users.Serializer import UserRegSerializer, LoginSerializer, UserpwdSerializer
from users.models import SmsModel, UserToken

# 设置日志
logger = logging.getLogger('django')


# 验证码的视图类
class SmscodeView(APIView):

    # 生成随机的四位数验证码
    def get_varify_code(self):
        resource_ = '0123456789'
        res_str = ''
        for i in range(4):
            res_str += random.choice(resource_)  # 生成4位数的随机验证码
        return res_str

    def post(self, request):
        data = request.data
        # 获取手机号
        phone = data.get('phone')

        # 验证码获取
        code = self.get_varify_code()
        # code = '1234'

        # 发送短信 ucloud
        result_data = send_sms(phone, code)
        # result_data = {'Message': 'Send success'}

        # 使用 celery 异步发送短信
        # result = send_sms_code.delay(mobile, code)
        if result_data['Message'] == 'Send success':
            result = 0
        else:
            result = 1

        """
        使用 celery 异步发送短信的步骤
        1、安装celery包，（如果在window下使用还需要安装gevent包）
        2、需要配置 celery的环境（config.py main.py tasks.py）
        3、把短信发送的接口放入 sms 文件夹中
        4、启动celery任务，启动成功后就可以发短信了。
        windows下启动命令：
        启动任务：celery -A celery_tasks.main worker -l info -P gevent
        linux下启动命令：
        启动任务：celery -A celery_tasks.main worker -l info
        守护进程：celery multi start -A celery_tasks.main worker -l info --logfile=./logs/celery.log
        5、注册用户，发送验证码。
        """

        if result != 0:
            logger.error('%s验证码%s发送失败' % (phone, code))
            return Response({"message": "%s验证码发送失败" % (phone), 'data': "%s" % (code)}, status=401)
        else:
            SmsModel.objects.create(phone=phone, code=code)
            redis_conn = get_redis_connection('verify_codes')  # 实例化一个redis连接对象
            redis_pipeline = redis_conn.pipeline()  # 实例化一个redis的管道对象
            redis_pipeline.setex('sms_%s' % phone, 85, code)  # 通过管道设置redis中的键值对数据
            redis_pipeline.execute()  # 通过管道提交到redis中去
            logger.info('%s验证码%s发送成功' % (phone, code))
            return Response({"message": "%s验证码发送成功" % (phone), 'data': "%s" % (code)}, status=201)


# 注册视图
class RegisterView(APIView):

    def post(self, request):
        # print(request.data)  # 前端信息
        serializer = UserRegSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 获取注册所生成的用户
        user = serializer.save()

        # drf-jwt生成
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # 创建token
        UserToken.objects.create(user=user, token=token)

        # 数据信息返回给前端
        dic = serializer.validated_data
        del dic['code']
        del dic['username']
        del dic['password']
        dic['token'] = token
        # 用户认证后头部必须要带的参数
        headers = {'Authorization': 'Bearer %s' % token}
        # print(data)
        # print(serializer.validated_data)
        return Response(dic, status=201, headers=headers)


# 获取用户模型，django的认证用户模型
User = get_user_model()


# 忘记密码的视图
class find_pwdView(APIView):

    # 根据请求手机号获取用户信息
    def post(self, request):
        # print(request.data)
        serializer = UserpwdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = request.data.get('phone')
        # 确认后更新用户密码
        user = User.objects.get(phone=phone)
        # 对明文密码进行加密
        user.password = make_password(request.data.get('password'))
        user.save()

        logger.info('手机号%s所在用户密码修改成功' % (phone))
        return Response({"message": "手机号%s所在用户密码修改成功" % (phone)}, status=201)


# 手机号验证码登录
class LoginView(APIView):

    # 根据请求手机号获取用户信息
    def post(self, request):
        # 用户对象，来自请求，通过验证方法之后所返回的用户对象，没有通过认证的用户为匿名用户
        # print(request.data)  # 前端信息
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取当前手机号所在的用户
        user = User.objects.get(phone=request.data.get('phone'))

        # drf-jwt生成
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 数据信息返回给前端
        data = serializer.validated_data
        del data['code']
        data['user_id'] = user.id
        data['token'] = token
        headers = {'Authorization': 'Bearer %s' % token}
        # print(data)
        # print(serializer.validated_data)
        return Response(data, status=201, headers=headers)
