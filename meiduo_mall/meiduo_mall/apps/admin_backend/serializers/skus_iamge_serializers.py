from rest_framework import serializers

from goods.models import SKUImage, SKU

from fdfs_client.client import Fdfs_client

from django.conf import settings


class SKUSImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = SKUImage

        fields = ["id", "image", "sku", "sku_id"]

    def create(self, validated_data):
        image = validated_data.pop("image")

        coon = Fdfs_client(settings.FAST_CONFIG_PATH)

        content = image.read()

        result = coon.upload_appender_by_buffer(content)

        if not result.get("Status") == "Upload successed.":
            raise serializers.ValidationError("上传失败")

        url = result.get("Remote file_id")

        validated_data["image"] = url

        return super().create(validated_data)

    def update(self, instance, validated_data):

        image = validated_data.pop("image")

        coon = Fdfs_client(settings.FAST_CONFIG_PATH)

        content = image.read()

        result = coon.upload_appender_by_buffer(content)

        if not result.get("Status") == "Upload successed.":
            raise serializers.ValidationError("上传失败")

        url = result.get("Remote file_id")

        print(url)
        instance.image = url

        # return instance
        return super().update(instance, validated_data)


class SKUSSserializer(serializers.ModelSerializer):
    class Meta:
        model = SKU

        fields = ["id", "name"]
