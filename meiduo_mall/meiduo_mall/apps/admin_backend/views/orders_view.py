from rest_framework.viewsets import ModelViewSet

from admin_backend.page_tool import Page_tool
from admin_backend.serializers.orders_serializers import OrdersModelSerializers

from orders.models import OrderInfo


class OrdersModelViewSet(ModelViewSet):
    queryset = OrderInfo.objects.order_by("create_time")

    serializer_class = OrdersModelSerializers

    pagination_class = Page_tool

    def get_queryset(self):
        keyword = self.request.query_params.get("keyword")

        if keyword:
            return self.queryset.filter(order_id__contains=keyword)

        return self.queryset
