from rest_framework import serializers

from goods.models import SKU, SPUSpecification, GoodsCategory, SPU, SpecificationOption, SKUSpecification


class SpecsSerializers(serializers.ModelSerializer):
    option_id = serializers.IntegerField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = ["spec_id", "option_id"]


class SkusSerializers(serializers.ModelSerializer):
    # 商品SKU名称
    spu = serializers.StringRelatedField()

    # 商品sku_id
    spu_id = serializers.IntegerField()

    # 三级分类名称
    category = serializers.StringRelatedField()

    # 三级分类id
    category_id = serializers.IntegerField()

    # 分类选项
    specs = SpecsSerializers(many=True)

    class Meta:
        model = SKU

        fields = "__all__"

    def create(self, validated_data):

        spec_option = validated_data.pop("specs")

        sku = super().create(validated_data)

        for temp in spec_option:
            print(temp)
            temp['sku_id'] = sku.id

            SKUSpecification.objects.create(**temp)

        return sku

    def update(self, instance, validated_data):

        spec_option = validated_data.pop("specs")

        for temp in spec_option:
            print(temp)
            m = SKUSpecification.objects.get(sku_id=instance.id, spec_id=temp["spec_id"])

            m.option_id = temp["option_id"]

            m.save()

        return super().update(instance, validated_data)


class GoodsCateforySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory

        fields = ["id", "name"]


class SPUSerializers(serializers.ModelSerializer):
    class Meta:
        model = SPU

        fields = ["id", "name"]


# ------------------------------------------------------------------
class SPUOptionSerializers(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption

        fields = ["id", "value"]


class SPUSpecsSerializers(serializers.ModelSerializer):
    options = SPUOptionSerializers(read_only=True, many=True)

    spu = serializers.StringRelatedField(read_only=True)

    spu_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SPUSpecification

        fields = ['id', 'name', 'spu', 'spu_id', 'options']
