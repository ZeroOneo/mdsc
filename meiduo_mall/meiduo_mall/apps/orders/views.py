from decimal import Decimal
from django import http
from django.core.paginator import Paginator, EmptyPage

from django.shortcuts import render
from django.utils import timezone
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import Lr
from users.models import Address, User
from django_redis import get_redis_connection
from goods.models import SKU
from .models import OrderInfo, OrderGoods
from django.db import transaction
import logging
import json

logger = logging.getLogger(name="info")


class OrderSettlementView(Lr):
    """渲染订单视图"""

    def get(self, request):

        # 获取用户
        user = request.user

        # 获取收货地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except User.DoesNotExist:
            addresses = None

        # 连接redis
        redis_conn = get_redis_connection("carts")

        # 查hash  {sku_id: count}
        redis_cart = redis_conn.hgetall("carts_%s" % user.id)

        # 查set  selected{sku_id}
        selected_ids = redis_conn.smembers("selected_%s" % user.id)

        # 构建carts = {sku_id:count}
        carts = {}
        for sku_id_bytes in selected_ids:
            carts[int(sku_id_bytes)] = int(redis_cart[sku_id_bytes])

        # 初始化数据
        total_count = 0
        total_amount = Decimal("0.00")
        freight = Decimal("200.99")

        # 查询商品
        skus = SKU.objects.filter(id__in=carts.keys())
        for sku in skus:
            sku.count = carts[sku.id]
            sku.amount = sku.count * sku.price
            total_count += sku.count
            total_amount += sku.price * sku.count

        # 渲染界面
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }

        return render(request, "place_order.html", context)


class OrderCommitView(Lr):
    """提交订单视图"""

    def post(self, request):
        """保存订单基本信息和商品信息"""

        # 取出参数 address pay_method
        json_data = json.loads(request.body.decode())
        address_id = json_data.get("address_id")
        pay_method = json_data.get("pay_method")

        # 校验参数是否全
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden("参数缺少")

        # 校验地址编号是准确
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden("地址不对")

        # 校验支付方式是否正确
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM["CASH"], OrderInfo.PAY_METHODS_ENUM["ALIPAY"]]:
            return http.HttpResponseForbidden("支付方式错误")

        # 获取登录用户
        user = request.user

        # 生成订单编号
        order_id = timezone.localtime().strftime("%Y%m%d%H%M%s") + ("%09d" % user.id)

        # 显式开启一个事物
        with transaction.atomic():

            # 创建失误保存点
            save_id = transaction.savepoint()

            # 暴力回滚
            try:

                # 保存订单基本信息
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_amount=Decimal("0"),
                    total_count=0,
                    freight=Decimal("200.99"),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        "ALIPAY"] else
                    OrderInfo.ORDER_STATUS_ENUM["UNSEND"],

                )

                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection("carts")
                redis_cart = redis_conn.hgetall("carts_%s" % user.id)
                selected = redis_conn.smembers("selected_%s" % user.id)
                carts = {}
                for sku_id in selected:
                    carts[int(sku_id)] = int(redis_cart[sku_id])

                sku_ids = carts.keys()

                # 遍历购物车中被勾选的商品信息
                for sku_id in sku_ids:

                    # 增加死循环 可以有多次机会
                    while True:
                        # 查询SKU信息
                        sku = SKU.objects.get(id=sku_id)

                        # 读取原始库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 判断sku库存
                        sku_count = carts[sku_id]
                        if sku_count > sku.stock:
                            # 事物回滚
                            transaction.savepoint_rollback(save_id)

                            # 提前响应
                            return http.JsonResponse({"code": RETCODE, "errmsg": "库存不足"})

                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.sku.save()

                        # 乐观锁更新库存和销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)

                        # 判断锁的状态
                        if result == 0:
                            # 返回空  重新下单
                            continue

                        # 修改SPU的销量
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        # 保存订单信息
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price
                        )

                        # 保存商品订单中的总价和总数量
                        order.total_count += sku_count
                        order.total_amount += (sku_count * sku.price)

                        # 下单成功跳出循环
                        break

                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
                print(order.total_amount, "----", order.freight)
            except Exception as e:
                logger.error(e)
                # 回滚
                transaction.savepoint_rollback(save_id)

                # 响应
                return http.JsonResponse({"code": RETCODE.DBERR, "errmsg": "下单失败"})

            # 订单提交成功 显式提交
            transaction.savepoint_commit(save_id)

        # 清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel("carts_%s" % user.id, *selected)
        pl.srem("selected_%s" % user.id, *selected)
        pl.execute()

        # 响应提交订单结果
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "下单成功", "order_id": order.order_id})


class OrderSuccessView(Lr):
    """订单提交成功视图"""

    def get(self, request):

        order_id = request.GET.get("order_id")
        payment_amount = request.GET.get("payment_amount")
        pay_method = request.GET.get("pay_method")

        # 校验订单
        try:
            OrderInfo.objects.get(order_id=order_id, pay_method=pay_method, total_amount=payment_amount)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden("无效订单")

        # 准备渲染数据
        context = {
            "order_id": order_id,
            "payment_amount": payment_amount,
            "pay_method": pay_method,
        }

        # 响应
        return render(request, "order_success.html", context)


class OrderShowView(Lr):
    """展示订单"""

    def get(self, request, page_num):

        user = request.user
        user_id = user.id
        # 获取所有订单

        order_qs = OrderInfo.objects.filter(user_id=user_id).order_by("-create_time")

        # 取出订单
        page_orders = []
        for order in order_qs:

            order_id = order.order_id

            # 获取商品列表

            order.sku_list = []

            order.status_name = order.ORDER_STATUS_CHOICES[order.status - 1][1]
            order.pay_method_name = order.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            goods = OrderGoods.objects.filter(order_id=order_id)

            # 获取单个商品添加到列表
            for good in goods:
                sku = SKU.objects.get(id=good.sku_id)
                sku.count = good.count
                sku.amount = (sku.price * good.count)
                order.sku_list.append(sku)

            page_orders.append(order)

        paginator = Paginator(order_qs, 2)

        try:
            # 获取指定页的数据
            page_orders = paginator.page(page_num)
        except EmptyPage:
            return http.HttpResponseForbidden("当前页不存在")

        # 获取总页数据
        total_page = paginator.num_pages

        context = {
            "page_orders": page_orders,
            "total_page": total_page,
            "page_num": page_num
        }

        return render(request, "user_center_order.html", context)
