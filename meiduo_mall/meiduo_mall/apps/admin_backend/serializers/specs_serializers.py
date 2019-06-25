from rest_framework import serializers
from goods.models import SPUSpecification


class SpecSerializers(serializers.ModelSerializer):
    """
    商品规格表管理
    """

    # 外键关联，提取spu_name
    spu = serializers.StringRelatedField(read_only=True)

    # 提取spu_id
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification

        fields = "__all__"



# 需获得的字段
# {
#                "id": "规格id",
#                 "name": "规格名称",
#                 "spu": "SPU商品名称",
#                 "spu_id": "SPU商品id"
#             },
