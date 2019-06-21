from datetime import timedelta

import pytz
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from admin_backend.serializers.goods_visit_serializer import GoodVisitSerializer
from goods.models import GoodsVisitCount
from users.models import *


# class HomeView(APIView):
#     """原始方法"""
#
#     def get(self,request):
#         """
#         当日总用户量
#         :param request:  None
#         :return:  {"count": "总用户量", "date": "日期"}
#         """
#
#         # 1 获取日期
#         date = timezone.now().date()
#
#         # 2 查出个数
#         count = User.objects.all().count()
#
#         return Response({
#             "count":count,
#             "date":date
#         })


class HomeViewSet(ViewSet):

    @action(methods=["get"], detail=False)
    def total_count(self, request):
        """
        使用视图集
        :param request:  None
        :return:  count   date
        """

        mytime = settings.TIME_ZONE
        date = timezone.now().astimezone(pytz.timezone(mytime)).date()

        count = User.objects.filter(is_active=True).count()

        return Response({
            "count": count,
            "date": date
        })

    @action(methods=["get"], detail=False)
    def day_increment(self, request):
        """
        日增用户数量
        :param request: None
        :return:  count  data
        """

        # 1 拿到今天的日期
        time_now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))
        # print("sh", time_now)

        utz_zero = timezone.now().replace(hour=0, minute=0, second=0)
        # print("utz", utz_zero)

        # 2 得到count

        count = User.objects.filter(date_joined__gte=utz_zero).count()

        return Response({
            "count": count,
            "date": time_now.date()
        })

    @action(methods=["get"], detail=False)
    def day_active(self, request):
        """
        日活跃用户
        :param request: None
        :return: count date
        """

        # 今天日期
        time_now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))

        # print("tz", timezone.now(), "\ntn", time_now)

        # utz零点
        utz_zero = timezone.now().replace(hour=0, minute=0, second=0)
        # print(utz_zero)

        # 过滤出活跃用户
        count = User.objects.filter(last_login__gte=utz_zero).count()

        return Response({
            "count": count,
            "date": time_now.date()
        })

    @action(methods=["get"], detail=False)
    def day_orders(self, request):
        """
        日下单用户数量
        :param request: None
        :return: date count
        """

        # 1 获得日期
        time_now = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))

        utz_zero = timezone.now().replace(hour=0, minute=0, second=0)

        # 2 获得数量
        count = User.objects.filter(orderinfo__create_time__gte=utz_zero).count()

        # 3 响应返回
        return Response({
            "date": time_now.date(),
            "count": count
        })

    @action(methods=["get"], detail=False)
    def month_increment(self, request):
        """
        30天内每天的新增用户量
        :param request:  None
        :return: date   count
        """

        # 1 获取29天前时间
        time_start = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)) - timedelta(days=29)
        # print(time_start)
        # 2 获取29天前的格林时间
        utz_time = timezone.now().replace(hour=0, minute=0, second=0) - timedelta(days=29)
        # print(utz_time)
        # 3 准备返回数据列表
        rt_ls = []

        # 4 遍历查询数据
        for i in range(30):
            rt_ls.append({
                "date": time_start.date() + timedelta(days=i),
                "count": User.objects.filter(
                    date_joined__gte=utz_time + timedelta(days=i), date_joined__lt=utz_time + timedelta(days=i + 1)

                ).count()
            })
        # print(rt_ls)
        # 5 响应返回
        return Response(rt_ls)

    @action(methods=["get"], detail=False)
    def goods_day_views(self, request):
        """
        日商品访问量
        :param request:  None
        :return:   {"category": "分类名称","count": "访问量"}
        """

        # 1 获取格林时间
        utz_time = timezone.now().date()
        # print(timezone.now())

        # 2 获取当天时间对应的数据
        goods = GoodsVisitCount.objects.filter(date=utz_time)
        # print(data)

        # 3 序列化
        sz_date = GoodVisitSerializer(goods, many=True)
        # print(sz_date)

        # list1 = []
        # for good in goods:
        #     count = good.count
        #     category = good.category.name
        #     list1.append({
        #     'count': count,
        #     'category': category
        # })

        # 5 响应返回
        return Response(sz_date.data)


