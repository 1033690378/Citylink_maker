import logging
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from Citylink_maker.settings import QQ_CLIENT_ID, QQ_CLIENT_SECRET, QQ_REDIRECT_URI
from OAuth.models import OAuthQQUser
from users.Serializer import LoginSerializer, UserRegSerializer
from OAuth.utils import generate_access_token, check_access_token
from users.models import UserToken

# 设置日志
logger = logging.getLogger('django')
# 获取用户模型，django的认证用户模型
User = get_user_model()


# 提供QQ登录扫码页面的视图
class QQAuthURLView(APIView):
    """提供QQ登录页面网址
    https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx
    """

    def get(self, request):
        # next表示从哪个页面进入到的登录页面，将来登录成功之后，就自动回到那个页面
        next = request.GET.get('next')

        # 获取请求登录页面网址
        oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET,
                        redirect_uri=QQ_REDIRECT_URI, state=next)

        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code': '0', 'errmsg': 'OK', 'login_url': login_url})


# QQ登录回调的视图，判断用户是否已绑定过账号，没绑定的绑定用户，没账号的注册用户
class QQAuthUserView(APIView):
    """用户扫码登录的回调处理"""

    def get(self, request):
        """Oauth2.0认证"""
        # 提取code请求参数
        code = request.GET.get('code')
        if not code:
            http.HttpResponseForbidden('缺少code')

        # 创建工具对象
        oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET,
                        redirect_uri=QQ_REDIRECT_URI)

        try:
            # 使用code向QQ服务器请求token
            access_token = oauth.get_access_token(code)
            # 使用token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logging.error(e)
            return http.HttpResponseServerError('Oauth2.0认证失败')

        # print('Oauth2.0认证成功')
        logger.info('Oauth2.0认证成功')
        # 使用openid判断该QQ用户是否绑定过商城用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # openid未绑定商城用户
            logger.info('未绑定过商城用户')
            access_token = generate_access_token(openid)
            return Response({'access_token': access_token}, status=201)
        else:
            # openid已绑定商城用户
            logger.info('已绑定商城用户')
            # print(oauth_user.user.phone)

            # 获取当前手机号所在的用户
            user = User.objects.get(phone=oauth_user.user.phone)
            # print(user)

            # drf-jwt生成
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            # 数据信息返回给前端
            data = {'phone': user.phone, 'user_id': user.id, 'token': token}
            headers = {'Authorization': 'Bearer %s' % token}
            # print(data)
            return Response(data, status=201, headers=headers)

    def post(self, request):
        """用户绑定到openid"""
        # 获取未登录用户是否有账号
        data = request.data.get('data')

        # 如果有账号的了就登录绑定
        if data == "1":
            '''数据是{data:1,phone,code,access_token}'''
            # 前端信息
            # print(request.data)
            # 登录该用户
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # 获取当前手机号所在的用户
            user = User.objects.get(phone=request.data.get('phone'))

            # 解码出openid
            openid = check_access_token(request.data.get('access_token'))
            # 已存在用户绑定到openid
            oauth_qq_user = OAuthQQUser.objects.create(user=user, openid=openid)

            # drf-jwt生成
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            # 数据信息返回给前端
            response = serializer.validated_data
            del response['code']
            response['user_id'] = user.id
            response['token'] = token
            headers = {'Authorization': 'Bearer %s' % token}
            # print(response)
            # print(serializer.validated_data)
            return Response(response, status=201, headers=headers)

        # 否则就是去注册用户
        else:
            '''数据是{data:2,username,phone,password,password1,code,access_token}'''
            # 前端信息
            # print(request.data)
            serializer = UserRegSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # 获取注册所生成的用户
            user = serializer.save()

            # 解码出openid
            openid = check_access_token(request.data.get('access_token'))
            # 已存在用户绑定到openid
            oauth_qq_user = OAuthQQUser.objects.create(user=user, openid=openid)

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
