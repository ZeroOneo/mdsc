from rest_framework import serializers

from goods.models import GoodsChannel, GoodsCategory, GoodsChannelGroup


class GoodsChannelSerializers(serializers.ModelSerializer):
    group = serializers.StringRelatedField()

    group_id = serializers.IntegerField()

    category = serializers.StringRelatedField()

    category_id = serializers.IntegerField()

    class Meta:
        model = GoodsChannel

        fields = ["id", "group", "group_id", "category", "category_id", "url", "sequence"]

        # this.ChannelsForm.group_id = dat.data.group_id;
        # this.ChannelsForm.category_id = dat.data.category_id;
        # this.ChannelsForm.url = dat.data.url;
        # this.ChannelsForm.sequence = dat.data.sequence;


class Channel_typesSerializers(serializers.ModelSerializer):
    class Meta:
        model = GoodsChannelGroup

        fields = ["id", "name"]


class GoodsCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory

        fields = ["id", "name"]
