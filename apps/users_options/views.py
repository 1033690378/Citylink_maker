import logging
from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView, UpdateAPIView, ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users_options.Serializer import UserUpdateSerializer, AddressSerializer
from users_options.models import UserAddress

# 设置日志
logger = logging.getLogger('django')
# 从用户的子应用中获取用户模型
User = get_user_model()


# 用户个人信息的视图
class UserInfoView(ListAPIView, UpdateAPIView):
    """
    实现增加和获取信息，取决于你所继承的是哪个类：
    ListAPIView    帮你实现了 Get请求，如果继承这个类，就可以获取地址信息。
    ListCreateAPIView   帮你把 Post和Get请求都实现了，既可以创建也可以获取信息。
    """
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    # 在修改之前先做一下用户的认证
    permission_classes = [IsAuthenticated]

    # 获取当前的用户是谁
    def get_object(self):
        return self.request.user

    # 重写list方法，通过用户ID来过滤每个用户的个人信息
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(phone=request.user.phone).all()
        # print(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=201)

    # 修改个人信息(重写 UpdateAPIView 中的 update 方法)
    def update(self, request, *args, **kwargs):
        # 获取前端的数据用于修改数据库中的内容
        data = request.data
        # print(data)
        # 获取需要修改的个人信息
        obj = self.get_queryset().filter(phone=request.user.phone)
        # print(obj)

        # 反序列化，用户数据更新操作
        serializer = self.get_serializer(data=data, instance=obj.first())
        # 校验数据
        serializer.is_valid(raise_exception=True)
        # 修改信息保存
        serializer.save()
        return Response({"message": "个人信息更新成功"}, status=201)


# 用户的收货地址
class AddressView(ListCreateAPIView, UpdateAPIView, DestroyAPIView):
    """
    实现增加和获取收货地址，取决于你所继承的是哪个类：
    CreateAPIView  帮你实现了 Post请求，你如果继承这个类，就可以新增地址。
    ListAPIView    帮你实现了 Get请求，如果继承这个类，就可以获取地址信息。
    ListCreateAPIView   帮你把 Post和Get请求都实现了，既可以创建也可以获取信息。
    """
    # 用户收货地址的创建和查询
    queryset = UserAddress.objects.all()
    serializer_class = AddressSerializer

    # 在修改之前先做一下用户的认证
    permission_classes = [IsAuthenticated]

    # 获取当前的用户是谁
    def get_object(self):
        return self.request.user

    # 重写list方法，通过用户ID来过滤每个用户的收货地址
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user_id=request.user.id).all()
        # print(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=201)

    # 修改收货地址的信息(重写 UpdateAPIView 中的 update 方法)
    def update(self, request, *args, **kwargs):
        # 获取前端的数据用于修改数据库中的内容
        address_id = kwargs.get('pk')  # 获得修改用户地址的对应id
        data = request.data  # 获取前端的数据用于修改数据库中的内容
        # print(data)
        # 通过过滤查询来找到需要修改的那一条收货地址信息
        obj = self.get_queryset().filter(id=address_id)
        # print(obj)

        # 反序列化
        serializer = self.get_serializer(data=data, instance=obj.first())
        serializer.is_valid(raise_exception=True)  # 校验数据
        serializer.save()
        return Response({"message": "收货地址更新成功"}, status=201)

    # 重写 DestroyAPIView 类中的 destroy方法
    def destroy(self, request, *args, **kwargs):
        # 获取需要删除的收货地址id值
        address_id = kwargs.get('pk')
        # 在查询集中筛选需要删除的那个收货地址信息，并执行删除操作
        obj = self.get_queryset().filter(id=address_id).delete()
        # 删除成功后给前端返回信息
        return Response({"messages": "收货地址删除成功"}, status=201)
