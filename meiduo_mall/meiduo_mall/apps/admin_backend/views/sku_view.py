from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from admin_backend.page_tool import Page_tool
from admin_backend.serializers.sku_serializers import SkusSerializers, GoodsCateforySerializer, SPUSerializers, \
    SPUSpecsSerializers
from goods.models import SKU, GoodsCategory, SPU, SPUSpecification


class SkusModelView(ModelViewSet):
    """sku展示"""

    # 获取查询集
    queryset = SKU.objects.order_by("id")

    # 获取序列化器
    serializer_class = SkusSerializers

    # 分页器
    pagination_class = Page_tool

    def get_queryset(self):
        # 提取keyword
        keyword = self.request.query_params.get("keyword")

        # 判断过滤
        if keyword:
            return self.queryset.filter(name__contains=keyword)
        return self.queryset.all()


class CategoryView(ListAPIView):
    """
    商品类别展示
    """

    # 查询集为parent_id 大于37
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)

    # 序列化器
    serializer_class = GoodsCateforySerializer


class SimpleView(ListAPIView):
    """spu商品"""
    queryset = SPU.objects.all()

    serializer_class = SPUSerializers


class SpecsView(ListAPIView):
    """
    前端传pk  后端响应pk对于sku编号
    """

    queryset = SPUSpecification.objects.all()

    serializer_class = SPUSpecsSerializers

    def get_queryset(self):
        spu_id = self.kwargs.get('pk')

        return self.queryset.filter(spu_id=spu_id)
