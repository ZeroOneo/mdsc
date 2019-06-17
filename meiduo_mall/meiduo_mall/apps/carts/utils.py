import pickle, base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    # 获取cookie
    cart_str = request.COOKIES.get("carts")

    # 判断是否为空
    if cart_str is None:
        return response

    # 解密  str -----b----------64b-------dict
    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    # 创建redis连接对象  管道
    redis_conn = get_redis_connection("carts")
    pl = redis_conn.pipeline()

    # 遍历cookie字典  合并到redis
    for sku_id in cart_dict:
        # hash中sku_id存在就覆盖,没有就添加
        pl.hset("carts_%s" % user.id, sku_id, cart_dict[sku_id]["count"])
        # 往set中添加selected sku_id
        if cart_dict[sku_id]["selected"]:
            # 勾选的
            pl.sadd("selected_%s" % user.id, sku_id)
        else:
            # 未勾选的
            pl.srem("selected_%s" % user.id, sku_id)

    # 执行管道
    pl.execute()

    # 删除cookie购物车
    response.delete_cookie("carts")
