import json
import logging, re

from meiduo_mall.utils import sinaweibopy3
from users.models import User
from django_redis import get_redis_connection

# from users.models import User
from django.conf import settings
from .utils import generat_openid_signature, check_openid_signature
from django.contrib.auth import login

from .models import OAuthQQUser, OAuthSinaUser
from django import http

from django.shortcuts import render, redirect
from QQLoginTool.QQtool import OAuthQQ
from django.views import View

from meiduo_mall.utils.response_code import RETCODE
from carts.utils import merge_cart_cookie_to_redis

logger = logging.getLogger('django')


# 1.提供QQ登陆路由
# 2.获取access token
# 3.获取openid


class QQAuthURLView(View):
    """提取QQ登陆路由"""

    def get(self, request):
        # 获取next参数，获取用户从哪个界面登陆到login里面
        next = request.GET.get('next') or '/'

        # QQ_CLIENT_ID = '101518219'
        # QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
        # QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

        # 创建QQSDK对象
        auth_qq = OAuthQQ(client_id='101518219',
                          client_secret='418d84ebdc7241efb79536886ae95224',
                          redirect_uri='http://www.meiduo.site:8000/oauth_callback',
                          state=next
                          )
        # 调用get_qq_url方法获取拼接好的qq登陆url
        login_url = auth_qq.get_qq_url()
        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class QQAuthView(View):
    """QQ登陆成功的回调处理"""

    def get(self, request):
        # 1.获取查询参数的code
        code = request.GET.get('code')
        # 2.校验
        if code is None:
            return http.HttpResponseForbidden('缺少code参数')
        # 3.再次创建SDK对象
        auth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                          client_secret=settings.QQ_CLIENT_SECRET,
                          redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 4.调用SDK中的get_access_token获取access_token
            access_token = auth_qq.get_access_token(code)
            # 5.调用SDK中的get_open_id获取openid
            openid = auth_qq.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('QQ的OAuth2.0认证失败')
        try:
            # 查询表中是否有当前这个openid
            oauth_qq = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果没有查询到openid，说明此QQ是一个新的还没有绑定过的美多用户，应该去绑定
            openid = generat_openid_signature(openid)
            return render(request, 'oauth_callback.html', {'openid': openid})
        else:
            # 如果查询到openid，说明之前已绑定，直接代表登陆成功
            # 获取openid所关联的用户
            user = oauth_qq.user
            # 保持状态
            login(request, user)
            # 获取用户界面来源
            next = request.GET.get('state')
            # 创建响应对象及重定向
            response = redirect(next or '/')
            # 向cookie中设置username以备在状态栏现实登陆用户的用户名
            response.set_cookie('usernname', user.username, max_age=300)
            # 在此处就作合并购物车
            merge_cart_cookie_to_redis(request, response)
            # 响应
            return response

    def post(self, request):
        """绑定用户处理"""
        # 1.接受数据
        query_dict = request.POST
        mobile = query_dict.get('mobile')
        password = query_dict.get('password')
        sms_code = query_dict.get('sms_code')
        openid = query_dict.get('openid')
        # 2.校验
        if all([mobile, password, sms_code, openid]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('您输入的手机号格式不正确')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 连接redis数据库获取短信标识
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_code_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '短信验证码已失效'})
        if sms_code_server.decode() != sms_code:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '请输入正确的验证码'})
        # 对openid进行解密
        openid = check_openid_signature(openid)
        if openid is None:
            return http.HttpResponseForbidden('openid无效')

        # 3.处理逻辑
        # 先判断用户是否存在，如果用户的手机号在user表中查不到创建一个新的用户
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 表示没有该用户，需要创建一个新的用户
            user = User.objects.create_user(mobile=mobile, password=password, username=mobile)

        else:
            # 用户存在，判断该用户的密码是否正确
            if user.check_password(password) is False:
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或者密码错误'})
            # openid和用户绑定
            OAuthQQUser.objects.create(
                openid=openid,
                user=user
            )

            login(request, user)  # 保持状态
            next = request.GET.get('state')  # 获取用户界面来源
            response = redirect(next or '/')  # 创建响应对象及重定向
            # 向cookie中设置username以备在状态栏显示用户的用户名
            response.set_cookie('username', user.username, max_age=300)
            # 在此处就作合并购物车
            merge_cart_cookie_to_redis(request, response)
            # 4.响应
            return response


class WBAuthURLView(View):
    """提供微博登录url"""

    def get(self, request):
        next = request.GET.get("next") or "/"

        # 实例化对象
        auth_sina = sinaweibopy3.APIClient(
            app_key=settings.APP_KEY,
            app_secret=settings.APP_SECRET,
            redirect_uri=settings.CALLBACK_URL
        )
        # 获取url
        login_url = auth_sina.get_authorize_url()

        # 响应结果  获取请求的url
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "login_url": login_url})


class WBCallBackView(View):
    """返回美多"""

    def get(self, request):
        """获取code"""
        code = request.GET.get("code")

        # code没有获取到
        if code is None:
            return http.HttpResponseForbidden("缺少code")

        # 实例化对象
        auth_sina = sinaweibopy3.APIClient(
            app_key=settings.APP_KEY,
            app_secret=settings.APP_SECRET,
            redirect_uri=settings.CALLBACK_URL
        )
        try:
            # 获取access_token
            dict = auth_sina.request_access_token(code)

        except Exception as e:
            logger.error(e)

            return http.HttpResponseServerError("wb的OAuth2.0认证失败")

        try:
            access_token = dict.access_token
            expires_in = dict.expires_in
            uid = dict.uid

        except Exception as e:
            return http.HttpResponseServerError("获取参数失败")

        # 判断uid是否绑定过用户
        try:
            user = OAuthSinaUser.objects.get(uid=uid)
        except OAuthSinaUser.DoesNotExist:
            # 没绑定时  跳转到绑定页面　带上身份证 uid

            uid = generat_openid_signature(uid)
            print(uid,"uid")
            response = render(request, "sina_callback.html")
            response.set_cookie("access_token", access_token, max_age=settings.SESSION_COOKIE_AGE)
            response.set_cookie("uid", uid, max_age=settings.SESSION_COOKIE_AGE)

            return response

        else:
            sina_user = user.user

            # 状态保持
            login(request, sina_user)

            # 重定向
            next = request.GET.get("state")
            response = redirect(next or "/")

            # 设置cookie
            response.set_cookie("username", sina_user.username, max_age=settings.SESSION_COOKIE_AGE)

            # 合并购物车
            merge_cart_cookie_to_redis(request=request, user=sina_user, response=response)

            # 响应结果
            return response


class WBUserView(View):

    def get(self, request):
        code = request.GET.get("code")
        access_token = request.COOKIES.get("access_token")

        data = {
            "access_token": access_token,
        }

        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "data": data})


    def post(self, request):
        """提交表单"""

        data_str = request.body.decode()

        data_dict = json.loads(data_str)

        mobile = data_dict.get("mobile")

        image_code = data_dict.get("image_code")
        sms_code = data_dict.get("sms_code")
        password = data_dict.get("password")
        uid = request.COOKIES.get("uid")

        print(1)
        # ４判断数据是否齐全
        if all([mobile, password, sms_code, uid]) is None:
            return http.HttpResponseForbidden("参数不全")

        if not re.match(r"^1[3-9]\d{9}", mobile):
            print(type(mobile))
            return http.HttpResponseForbidden("手机号码不对")

        if not re.match(r"^[a-zA-Z0-9_-]{8,20}$", password):
            return http.HttpResponseForbidden("密码不符合规范")
        print(2)
        # 验证短信验证码
        redis_connection = get_redis_connection("verify_code")
        # 获取redis短信验证码
        sms_code_server = redis_connection.get("sms_%s" % mobile)

        print(sms_code_server)

        # 校验短信验证码是否过期
        if sms_code_server is None:
            return http.HttpResponseForbidden("短信验证码过期")

        print(sms_code_server)
        # 转换成字符串，比对结果
        sms_code_server = sms_code_server.decode()
        if sms_code_server.lower() != sms_code.lower():
            return http.HttpResponseForbidden("短信验证码不对")

        # 解密uid
        uid = check_openid_signature(uid)
        print(uid)
        if uid is None:
            return http.HttpResponseForbidden("uid无效")

        # 根据手机号查看用户是否已经绑定过
        try:
            user = User.objects.get(mobile=mobile)
            print(user)
        except User.DoesNotExist:
            user = User.objects.create_user(mobile=mobile, password=password, username=mobile)
            print(user,"2")
        else:
            # 检验老用户密码
            if user.check_password(password) is False:
                return render(request, "sina_callback.html", {"account_errmsg": "用户名或密码错误"})
        print("heheh")
        # 将uid和用户绑定
        OAuthSinaUser.objects.create(uid=uid, user=user)
        # 状态保持
        login(request, user)
        next = request.GET.get("state")
        response = redirect(next or "/")
        # 向cookie中设置username以显示名字
        response.set_cookie("username", user.username, max_age=settings.SESSION_COOKIE_AGE)

        # 合并购物车
        merge_cart_cookie_to_redis(request=request, response=response)

        return response
