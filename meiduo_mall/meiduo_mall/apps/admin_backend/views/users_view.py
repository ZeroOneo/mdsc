from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView
from rest_framework.response import Response

from admin_backend.page_tool import Page_tool
from admin_backend.serializers.users_serializers import ShowUsersModelSerializer
from users.models import User


class UserView(ListAPIView, CreateAPIView):
    # 处理的数据集
    queryset = User.objects.all()

    # 序列化器
    serializer_class = ShowUsersModelSerializer

    # 配置分页器
    pagination_class = Page_tool

    def get_queryset(self):
        """
        实现自定义获得的数据集
        :return: 数据集
        """

        # 判断字符串参数中有没有keyword值
        keyword = self.request.query_params.get("keyword")

        if keyword:
            # 有的话过滤
            return self.queryset.filter(username__contains=keyword)

        # 没有默认返回
        return self.queryset.all()


# class UserView(GenericAPIView):
#     # 1 获取查询集
#     queryset = User.objects.all()
#
#     # 2 序列化器
#     serializer_class = ShowUsersModelSerializer
#
#     # 3 分页器
#     pagination_class = Page_tool
#
#     def get_queryset(self):
#         """
#         实现自定义获得的数据集
#         :return: 数据集
#         """
#
#         # 判断字符串参数中有没有keyword值
#         keyword = self.request.query_params.get("keyword")
#
#         if keyword:
#             # 有的话过滤
#             return self.queryset.filter(username__contains=keyword)
#
#         # 没有默认返回
#         return self.queryset.all()
#
#     def get(self,request):
#         queryset = self.get_queryset()
#         page = self.paginate_queryset(queryset)
#
#         if page:
#             page_serializer = self.get_serializer(page, many=True)
#
#             return self.get_paginated_response(page_serializer.data)
#
#         serializer = self.get_paginated_response(queryset, many=True)
#
#         return Response(serializer.data)
