
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django.contrib.auth.models import Group, Permission

from admin_backend.serializers.groups_serializers import GroupsSerializers

from admin_backend.page_tool import Page_tool
from admin_backend.serializers.permission_serializers import ShowPermissionSerializers


class GroupsModelViewSet(ModelViewSet):
    queryset = Group.objects.order_by("id")

    serializer_class = GroupsSerializers

    pagination_class = Page_tool


    @action(methods=["get"],detail=False)
    def simple(self, request):
        instance = Permission.objects.all()

        s = ShowPermissionSerializers(instance, many=True)

        return Response(s.data)
