from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from django.contrib.auth.models import Permission


class PermissionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Permission

        fields = "__all__"


class ShowPermissionSerializers(serializers.ModelSerializer):

    class Meta:
        model = ContentType

        fields = ["id", "name"]