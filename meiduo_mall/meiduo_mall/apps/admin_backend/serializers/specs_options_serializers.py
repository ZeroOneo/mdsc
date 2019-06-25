from rest_framework import serializers
from goods.models import SpecificationOption, SPUSpecification


class SpecsOptionsSerializers(serializers.ModelSerializer):

    spec = serializers.StringRelatedField(read_only=True)

    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption

        fields = "__all__"


# 需要的参数
# "id": "选项id",
# "value": "选项名称",
# "spec": "规格名称",
# "spec_id": "规格id"a

class SpecsSimpleSerializers(serializers.ModelSerializer):
    class Meta:
        model = SPUSpecification

        fields = "__all__"

        # "id": "规格id",
        # "name": "规格名称"
