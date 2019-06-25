from rest_framework.viewsets import ModelViewSet

from admin_backend.page_tool import Page_tool
from goods.models import Brand

from admin_backend.serializers.goodsBrandsSerializers import GoodsBrandsSerializers


class GoodBrandsModelViewSet(ModelViewSet):
    queryset = Brand.objects.order_by("id")

    serializer_class = GoodsBrandsSerializers

    pagination_class = Page_tool
