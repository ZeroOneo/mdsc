from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django import http

from contents.utils import get_categories
from goods.models import GoodsCategory, SKU, GoodsVisitCount
from goods.utils import get_breadcrumb
from meiduo_mall.utils.response_code import RETCODE


class ListView(View):
    """商品列表界面"""

    def get(self, request, category_id, page_num):

        # 根据id得到对象
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseNotFound("商品类别不存在")

        # 获取前端传入的排序规则
        sort = request.GET.get("sort")
        if sort == "price":
            sort_field = "price"
        elif sort == "hot":
            sort_field = "-sales"
        else:
            sort = "default"
            sort_field = "-create_time"

        # 获取当前三级类别中所有的上架的sku数据
        sku_qs = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        # 创建分页对象Paginator(要分页的所有数据,每页显示多个数据)
        paginator = Paginator(sku_qs, 5)

        try:
            # 获取指定页的数据
            page_skus = paginator.page(page_num)
        except EmptyPage:
            return http.HttpResponseForbidden("当前页不存在")

        # 获取总页数据
        total_page = paginator.num_pages

        # 需要渲染的数据
        context = {
            "categories": get_categories(),  # 频道分类
            "breadcrumb": get_breadcrumb(category),  # 面包屑导航
            "sort": sort,  # 排序字段
            "category": category,  # 第三级分类
            "page_skus": page_skus,  # 分页后数据
            "total_page": total_page,  # 总页数
            "page_num": page_num,  # 当前页码
        }
        # print(context)
        return render(request, "list.html", context)


class HotGoodsView(View):
    """爆品排行"""

    def get(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden("商品类别不存在")

        sku_qs = SKU.objects.filter(category=category, is_launched=True).order_by("-sales")[:2]
        hot_skus = []

        for sku in sku_qs:
            hot_skus.append({
                "id": sku.id,
                "name": sku.name,
                "price": sku.price,
                "default_image_url": sku.default_image.url
            })

        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "ok", "hot_skus": hot_skus})


class DetailView(View):
    """商品详情"""

    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, "404.html")

        category = sku.category
        spu = sku.spu

        """1 准备当前商品的规格选项列表"""
        # 获取出当前正在显示的sku商品的规格选项Id列表

        current_sku_spec_qs = sku.specs.order_by("spec_id")
        current_sku_options_ids = []
        for current_sku_spec in current_sku_spec_qs:
            current_sku_options_ids.append(current_sku_spec.option_id)

        """2 构造规则选择仓库
        {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        """
        # 构造规格选择仓库
        temp_sku_qs = spu.sku_set.all()
        # 选项仓库大字典
        spec_sku_map = {}
        for temp_sku in temp_sku_qs:
            temp_spec_qs = temp_sku.specs.order_by("spec_id")
            temp_sku_option_ids = []
            for temp_spec in temp_spec_qs:
                temp_sku_option_ids.append(temp_spec.option_id)
            spec_sku_map[tuple(temp_sku_option_ids)] = temp_sku.id

        """3 组合 并找到sku_id 绑定"""
        spu_spec_qs = spu.specs.order_by("id")
        for index, spec in enumerate(spu_spec_qs):
            spec_option_qs = spec.options.all()
            temp_option_ids = current_sku_options_ids[:]
            for option in spec_option_qs:
                temp_option_ids[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(temp_option_ids))
            spec.spec_options = spec_option_qs

        category = sku.category
        context = {
            "categories": get_categories(),  # 商品分类
            "breadcrumb": get_breadcrumb(category),  # 面包屑导航
            "sku": sku,  # 当前要显示的sku模型对象
            "spu": sku.spu,  # sku所属的spu
            "category": category,  # 当前的显示sku所属的三级列别
            "spec_qs": spu_spec_qs,  # 当前商品的所有规格数据
        }
        return render(request, "detail.html", context)


class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request, category_id):

        # 校验数据有效性
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden("参数无效")

        # 创建时间对象获取今天日期
        today = timezone.now()

        try:
            # 查看统计商品列表中查询当前的类别在今天有没有访问过的记录
            good_visit = GoodsVisitCount.objects.get(category=category, date=today)
        except GoodsVisitCount.DoesNotExist:

            # 不存在创建新纪录表明第一次访问
            good_visit = GoodsVisitCount(category=category)
            # good_visit = GoodsVisitCount()
            # good_visit.category = category

        # 访问量加一
        good_visit.count += 1
        good_visit.save()

        # 响应
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "ok"})
