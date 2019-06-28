from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from admin_backend.page_tool import Page_tool
from admin_backend.serializers.groups_serializers import GroupsSerializers
from users.models import User

from admin_backend.serializers.admins_serializers import AdminSerializers


class AdminModelViewSet(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)

    serializer_class = AdminSerializers

    pagination_class = Page_tool

    @action(methods=["get"], detail=False)
    def simple(self, request):
        instance = Group.objects.all()

        s = GroupsSerializers(instance, many=True)

        return Response(s.data)
