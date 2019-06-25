from rest_framework import serializers

from goods.models import Brand

class GoodsBrandsSerializers(serializers.ModelSerializer):

    class Meta:

        model = Brand

        fields = ["id","name","logo","first_letter"]

