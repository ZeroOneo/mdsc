from rest_framework import serializers
from goods.models import *


class SPUSerializers(serializers.ModelSerializer):
    # 品牌名称

    brand = serializers.StringRelatedField(read_only=True)

    # 品牌编号
    brand_id = serializers.IntegerField()

    # 一级类别
    category1_id = serializers.IntegerField()

    # 二级类别
    category2_id = serializers.IntegerField()

    # 三级类别
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU

        exclude = ("category1", "category2", "category3")


class BrandSerializers(serializers.ModelSerializer):
    class Meta:
        model = Brand

        fields = ["id", "name"]


class GoodsCategroy_1_Serializers(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory

        fields = "__all__"
