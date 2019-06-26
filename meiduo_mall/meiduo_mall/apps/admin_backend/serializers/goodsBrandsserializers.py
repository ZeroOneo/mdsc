from rest_framework import serializers
from fdfs_client.client import Fdfs_client
from django.conf import settings

from goods.models import Brand


class GoodsBrandsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Brand

        fields = ["id", "name", "logo", "first_letter"]

    def create(self, validated_data):
        logo = validated_data.pop("logo")

        conn = Fdfs_client(settings.FAST_CONFIG_PATH)

        content = logo.read()

        result = conn.upload_appender_by_buffer(content)

        if not result.get("Status") == "Upload successed.":
            raise serializers.ValidationError("上传失败")

        url = result.get("Remote file_id")

        validated_data["logo"] = url

        return super().create(validated_data)

    def update(self, instance, validated_data):

        logo = validated_data.pop("logo")

        conn = Fdfs_client(settings.FAST_CONFIG_PATH)

        content = logo.read()

        result = conn.upload_appender_by_buffer(content)

        if not result.get("Status") == "Upload successed.":
            raise serializers.ValidationError("上传失败")

        url = result.get("Remote file_id")

        print(instance.name)

        instance.logo = url

        instance.save()

        return instance
