from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission

from admin_backend.page_tool import Page_tool
from admin_backend.serializers.permission_serializers import PermissionSerializers, ShowPermissionSerializers


class PermissionModelViewSet(ModelViewSet):
    queryset = Permission.objects.all()

    serializer_class = PermissionSerializers

    pagination_class = Page_tool

    @action(method=["get"], detail=False)
    def content_types(self, request):
        instance = ContentType.objects.all()

        s = ShowPermissionSerializers(instance, many=True)

        return Response(s.data)
