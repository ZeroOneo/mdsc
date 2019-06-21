from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Page_tool(PageNumberPagination):
    """自定义分页器"""

    # 查询的key ?page=
    page_query_param = "page"

    # 指定当前页显示多少条
    page_size_query_param = "pagesize"

    # 每页显示多少条
    page_size = 5

    # 每页最多显示多少条
    max_page_size = 3

    def get_paginated_response(self, data):
        """
        自定义返回数据格式
        :param data: 分页子集的序列化结果
        :return: 对象
        """

        return Response({
            "count":self.page.paginator.count,  # 所有的數據
            "lists":data,   # 当前分页的数据子集
            "page":self.page.number,     # 第几页
            "pages":self.page.paginator.num_pages, # 总页数
            "pagesize":self.page_size   # 后台默认每页多少数据
        })