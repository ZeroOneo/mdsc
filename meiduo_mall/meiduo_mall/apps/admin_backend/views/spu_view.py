from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from goods.models import SPU, Brand, GoodsCategory
from admin_backend.serializers.spu_serializers import SPUSerializers, BrandSerializers, GoodsCategroy_1_Serializers
from admin_backend.page_tool import Page_tool


class SPUModelViewset(ModelViewSet):
    """
    spu新增
    """
    queryset = SPU.objects.all()

    serializer_class = SPUSerializers

    pagination_class = Page_tool


class SPUsimpleView(ListAPIView):
    """
    品牌id  name
    """
    queryset = Brand.objects.all()

    serializer_class = BrandSerializers


class SPUChannelView(ListAPIView):
    """
    一级分类
    """
    queryset = GoodsCategory.objects.filter(parent_id=None)

    serializer_class = GoodsCategroy_1_Serializers


class SPUchannel_23_View(ListAPIView):
    """
    二三级分类
    """

    serializer_class = GoodsCategroy_1_Serializers

    def get_queryset(self):

       pk = self.kwargs.get("pk")

       return GoodsCategory.objects.filter(parent_id=pk)