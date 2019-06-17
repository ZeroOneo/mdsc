from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from .models import User

import re


def get_user_by_account(account):
    """根据用户名或手机号获取user"""

    try:
        if re.match(r"1[3-9]\d{9}", account):
            #  匹配成功的话  输入的是手机号
            user = User.objects.get(mobile=account)

        else:
            #  匹配的是用户名
            user = User.objects.get(username=account)

    except User.DoesNotExist:

        return None

    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """多账号登录法二  : 自定义用户认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 根据传入的username 判断出是手机号还是用户名
        user = get_user_by_account(username)
        # 检查user是否存在以及所对应密码   user不存在返回none 调换位置会报错
        if user and user.check_password(password):
            return user


def email_active_url(user):
    """生成激活邮件连接并加密"""
    serializer = Serializer(settings.SECRET_KEY, 3600 * 24)
    # 构建发送的数据
    data = {"user_id": user.id, "email": user.email}
    # 对数据进行加密
    token = serializer.dumps(data).decode()

    # 构建ｕｒｌ
    send_url = settings.EMAIL_VERIFY_URL + "?token=" + token
    # 响应结果
    return send_url


def email_check_url(token):
    """解密邮件返回的资源"""
    serializer = Serializer(settings.SECRET_KEY, 3600 * 24)

    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get("user_id")

        email = data.get("email")
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        return user



