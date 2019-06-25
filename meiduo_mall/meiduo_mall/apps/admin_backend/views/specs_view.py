from rest_framework.viewsets import ModelViewSet
from admin_backend.page_tool import Page_tool
from admin_backend.serializers.specs_serializers import SpecSerializers
from goods.models import SPUSpecification


class SpecsModelViewSet(ModelViewSet):
    queryset = SPUSpecification.objects.order_by("spu_id")

    serializer_class = SpecSerializers

    pagination_class = Page_tool
