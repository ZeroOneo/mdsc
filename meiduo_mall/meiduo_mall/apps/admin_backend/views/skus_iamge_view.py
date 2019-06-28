from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from admin_backend.page_tool import Page_tool
from goods.models import SKUImage, SKU

from admin_backend.serializers.skus_iamge_serializers import SKUSImageSerializers,SKUSSserializer


class SKUSImageModelView(ModelViewSet):

    queryset = SKUImage.objects.order_by("id")

    serializer_class = SKUSImageSerializers

    pagination_class = Page_tool

    @action(methods=["get"],detail=False)
    def simple(self,request):

        instance = SKU.objects.all()

        s = SKUSSserializer(instance,many=True)

        return Response(s.data)