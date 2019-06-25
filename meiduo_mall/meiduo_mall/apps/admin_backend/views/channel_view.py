from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from admin_backend.page_tool import Page_tool
from admin_backend.serializers.channel_serializers import GoodsChannelSerializers, Channel_typesSerializers, \
    GoodsCategorySerializers
from goods.models import GoodsChannel, GoodsCategory, GoodsChannelGroup


class GoodsChannelsView(ModelViewSet):
    queryset = GoodsChannel.objects.order_by("id")

    serializer_class = GoodsChannelSerializers

    pagination_class = Page_tool

    @action(methods=["get"], detail=False)
    def channel_types(self, request):
        instance = GoodsChannelGroup.objects.all()

        s = Channel_typesSerializers(instance, many=True)

        return Response(s.data)

    def categories(self, request):
        instance = GoodsCategory.objects.filter(parent_id=None)

        s = GoodsCategorySerializers(instance, many=True)

        return Response(s.data)
