from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods
from goods.models import SKU


class SKUGoodsSerializers(serializers.ModelSerializer):
    class Meta:
        model = SKU

        fields = ["name", "default_image"]


class OrderGoodsModelSerializers(serializers.ModelSerializer):
    sku = SKUGoodsSerializers(read_only=True)

    class Meta:
        model = OrderGoods

        fields = ["sku", "count", "price"]


class OrdersModelSerializers(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    skus = OrderGoodsModelSerializers(read_only=True, many=True)

    class Meta:
        model = OrderInfo

        fields = "__all__"

# "order_id": "20181126102807000000004",
#         "user": "zxc000",
#         "total_count": 5,
#         "total_amount": "52061.00",
#         "freight": "10.00",
#         "pay_method": 2,
#         "status": 1,
#         "create_time": "2018-11-26T18:28:07.470959+08:00",
#         "skus": [
#             {
#                 "count": 1,
#                 "price": "6499.00",
#                 "sku": {
#                     "name": "Apple iPhone 8 Plus (A1864) 64GB 金色 移动联通电信4G手机",
#                     "default_image_url": "http:/
