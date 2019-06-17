import random

from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection
from . import contants
from celery_tasks.sms.tasks import ccp_send_sms_code

from meiduo_mall.libs.captcha.captcha import captcha
from django import http
import logging

logger = logging.getLogger()

from meiduo_mall.utils.response_code import RETCODE


class ImageCodeView(View):
    """验证码"""

    def get(self, request, uuid):
        # 生成图片验证码
        name, text, image = captcha.generate_captcha()

        # 保存图片验证码

        redis_conn = get_redis_connection("verify_code")
        redis_conn.setex('img_%s' % uuid, 300, text)

        return http.HttpResponse(image, content_type="image/jpg")


class SMSCodeView(View):
    """检查验证码是否正确"""

    def get(self, request, mobile):

        # 检验标记
        redis_conn = get_redis_connection("verify_code")

        send_flag = redis_conn.get("send_flag_%s" % mobile)

        #  检验是否有标记,有的话就是已经发过验证码
        if send_flag:
            return JsonResponse({"code": "dgjhc", "errmsg": "已经发过验证码了"})
        #  获取对象

        image_code_client = request.GET.get("image_code")

        uuid = request.GET.get("uuid")

        # 判断参数是否齐全
        if not all([image_code_client, uuid]):
            return JsonResponse({"code": RETCODE.NECESSARYPARAMERR, "errmsg": "缺少参数"})
        # 从redis中取出uuid

        image_code_server = redis_conn.get('img_%s' % uuid)

        # 拿出后删除redis中验证码使失效
        redis_conn.delete('img_%s' % uuid)

        # 检验验证码是否过期
        if not image_code_server:
            return JsonResponse({"code": RETCODE.IMAGECODEERR, "errmsg": "图形验证码失效"})

        # 比对图形验证码

        image_code_server = image_code_server.decode()
        print(image_code_client,"\n",image_code_server)
        if image_code_client.lower() != image_code_server.lower():

            return JsonResponse({"code": RETCODE.IMAGECODEERR, "errmsg": "图形验证码错误"})

        # 生成短信验证码

        sms_code = "%06d" % random.randint(0, 999999)

        logger.info(sms_code)
        print(sms_code)
        # 管道应用
        p1 = redis_conn.pipeline()
        # 保存短信验证码
        p1.setex("sms_%s" % mobile,60, sms_code)

        # 写入标记,设置60s过期
        p1.setex("send_flag_%s" % mobile, contants.SMS_CODE_REDIS_EXPIRES, 1)
        # info(redis_conn.get("send_flag%s")%mobile)

        # 执行管道
        p1.execute()
        #  发送短信验证码

        ccp_send_sms_code.delay(mobile, sms_code)

        return JsonResponse({"code": RETCODE.OK, "errmsg": "短信发送成功"})
