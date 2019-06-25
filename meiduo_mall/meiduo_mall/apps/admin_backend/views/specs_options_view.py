from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from admin_backend.page_tool import Page_tool
from admin_backend.serializers.specs_options_serializers import SpecsOptionsSerializers, SpecsSimpleSerializers
from goods.models import SpecificationOption, SPUSpecification


class SpecsOptionModelViewSet(ModelViewSet):
    """
    规格选项信息
    """
    queryset = SpecificationOption.objects.all()

    serializer_class = SpecsOptionsSerializers

    pagination_class = Page_tool


class SpecsSimpleView(ListAPIView):
    """
    展示SPU规格信息
    """
    queryset = SPUSpecification.objects.all()

    serializer_class = SpecsSimpleSerializers


class SpecsSimpleUpadateView(ListAPIView):
    """
    展示SPU规格信息
    """
    queryset = SPUSpecification.objects.all()

    serializer_class = SpecsSimpleSerializers

    def get_queryset(self):
        pk = self.kwargs.get("pk")

        return self.queryset.get(id=pk)
