from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseForbidden, JsonResponse
from carts.utils import merge_cart_cookie_to_redis
from goods.models import SKU
from oauth.utils import check_openid_signature, generat_openid_signature
from .models import User, Address
from django.contrib.auth import login, authenticate, mixins
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection
from celery_tasks.emails.tasks import send_verify_email
from .utils import email_active_url, email_check_url
from celery_tasks.sms.tasks import ccp_send_sms_code
from meiduo_mall.utils.views import Lr
import re, json
import logging, random

logger = logging.getLogger(name="info")


class RegisterView(View):
    """用户注册页面"""

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):

        request_data = request.POST
        print(request_data)
        username = request_data.get("username")

        password = request_data.get("password")
        password2 = request_data.get("password")
        mobile = request_data.get("mobile")
        sms_codes = request_data.get("sms_code")

        allow = request_data.get("allow")

        # 判断数据是否齐全
        if not all([username, password, password2, mobile, allow]):
            return HttpResponseForbidden("缺少必传参数")
        # 判断用户名是否合理
        if not re.match(r"^[a-zA-z0-9_]{5,20}$", username):
            return HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否输入正确
        if not re.match(r"^[0-9A-Za-z]{8,20}$", password):
            return HttpResponseForbidden("请输入8-20位的密码")
        # 判断两次密码是否一致
        if password != password2:
            return HttpResponseForbidden("两次输入的密码不一致")
        # 判断手机号输入是否正确
        if not re.match(r"^1[345789]\d{9}", mobile):
            return HttpResponseForbidden("您输入的手机号格式不正确")
        # 判断协议是否勾选  勾选返回True  否则返回False
        if not allow:
            return HttpResponseForbidden("请勾选用户协议")

        # 手机验证码 图形验证码
        redis_conn = get_redis_connection("verify_code")
        sms_code_server = redis_conn.get("sms_%s" % mobile)

        if not sms_code_server:
            return HttpResponseForbidden("短信验证码过期")

        if sms_code_server.decode() != sms_codes:
            return HttpResponseForbidden("验证码不匹配")
        #  保存用户数据

        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 保存用户状态
        login(request, user)

        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

        # return redirect("/")
        # return redirect(reverse('contents:index'))
        return response


class UserCountView(View):
    """判断用户名是否重复"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()

        return JsonResponse({"code": RETCODE.OK, "errmsg": "ok", "count": count})


class MobileCountView(View):
    """判断手机号是否重复"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({"code": RETCODE.OK, "errmsg": "ok", "count": count})


class LoginView(View):
    """用户登录视图"""

    def get(self, request):

        return render(request, "login.html")

    def post(self, request):

        username_c = request.POST.get("username")
        password_c = request.POST.get("password")
        remember_c = request.POST.get("remembered")

        #   ----- 多账号登录法一 : 修改内部源码匹配变量------
        # 使用正则匹配是否输入的是手机号
        # if re.match(r"1[3-9]\d{9}",username_c):
        #     #  将源码中的username替换为mobile
        #     User.USERNAME_FIELD = "mobile"

        # 判断user是否存在  不存在返回 none
        user = authenticate(username=username_c, password=password_c)
        # 将mobile 改回 username
        # User.USERNAME_FIELD = "username"

        if user is None:
            return render(request, "login.html", {"account_errmsg": "请输入正确的用户名或手机号"})

        login(request, user)

        if remember_c != "on":
            request.session.set_expiry(0)  # 设置会话结束,session_id 失效

        next = request.GET.get("next")  # 获取原始请求路径

        # 重定向首页,设置cookie  前端读取username 用于显示
        response = redirect(next or "/")
        # 设置首页cookie过期时长, cookie失效只能设置none
        response.set_cookie("username", username_c, max_age=settings.SESSION_COOKIE_AGE if remember_c else None)
        # 购物车合并

        merge_cart_cookie_to_redis(request, user, response)

        return response

        # 验证密码
        # user = User.objects.get(username=username_c)
        # try:
        #     user.check_password(password_c)
        # except:
        #     return render(request,"register.html")
        # else:
        #     return render(request,"index.html")


class LogoutView(View):
    """登出视图"""

    def get(self, request):
        logout(request)  # 使用django自带功能

        # 重定向到登录界面
        response = redirect("/login/")
        # 删除cookie
        response.delete_cookie("username")

        return response


class UserInfoView(mixins.LoginRequiredMixin, View):  # 法三 : 继承mixins.LoginRequiredMixin类
    """用户中心数据"""

    # 法二  使用类装饰器
    # @method_decorator(login_required)
    def get(self, request):
        # # 使用户登录后才能访问,没登录重定向到登录页面     法一:使用is_authenticated
        # if request.user.is_authenticated:   # django自带登录验证方法
        #
        #     return render(request,"user_center_info.html")
        #
        # else:
        #
        #     return redirect("/login/")

        return render(request, "user_center_info.html")


class EmailView(View):
    """设置用户邮箱"""

    def put(self, request):
        # 接收请求
        json_dict = json.loads(request.body.decode())
        email = json_dict.get("email")
        # 校验
        if not email:
            return JsonResponse({"code": RETCODE.EMAILERR, "errmsg": "缺少邮箱参数"})
        if not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return JsonResponse({"code": RETCODE.EMAILERR, "errmsg": "邮箱格式错误"})
        # 处理
        # 修改email的字段
        user = request.user

        User.objects.filter(username=user.username, email="").update(email=email)
        # 响应
        # 发激活邮件 celery
        # send_verify_email.delay(email, "www.baidu.com")
        # 加密邮件
        verify_url = email_active_url(user)
        send_verify_email.delay(email, verify_url)

        return JsonResponse({"code": RETCODE.OK, "errmsg": "设置邮箱成功"})


class VerifyEmailView(View):
    """核对邮箱"""

    def get(self, request):
        # 取出token
        token = request.GET.get("token")
        logger.info("code:", token)
        # 判断是否存在token
        if token is None:
            return HttpResponseForbidden("token不存在")
        # 解密token
        user = email_check_url(token)
        # 看用户是否存在
        if user is None:
            return HttpResponseForbidden("用户不存在")

        # 更改字段
        user.email_active = True
        user.save()

        return redirect("/info/")


class AddressView(View):
    """用户收货地址"""

    def get(self, request):
        """提供收货地址页面"""

        # 获取到用户
        login_user = request.user
        # 查询用户所对应地址信息,逻辑删除的不算
        addresses = Address.objects.filter(user=login_user, is_deleted=False)
        # 将地址信息序列化
        address_dict_list = []
        # 遍历取出所有地址字段
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            # 添加字典列表
            address_dict_list.append(address_dict)

        # 构建响应信息  默认地址id 和 地址字典列表
        context = {
            "default_address_id": login_user.default_address_id,
            "addresses": address_dict_list,
        }
        return render(request, "user_center_site.html", context)


class CreateAddressVIew(Lr):
    """新增地址"""

    def post(self, request):
        # 设置添加地址个数上限20
        count = request.user.addresses.count()
        if count >= 20:
            return JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '过多地址'})
        # 接收参数
        json_dict = json.loads(request.body.decode())
        title = json_dict.get("title")
        receiver = json_dict.get("receiver")
        province_id = json_dict.get("province_id")
        city_id = json_dict.get("city_id")
        district_id = json_dict.get("district_id")
        place = json_dict.get("place")
        mobile = json_dict.get("mobile")
        tel = json_dict.get("tel")
        email = json_dict.get("email")

        # 校验参数
        if not all([title, receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden("缺少必传参数")
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            return HttpResponseForbidden("号码错误")
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r"^[a-z0-9][\w\.\_]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
                return HttpResponseForbidden("邮箱格式错误")

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=title,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            logger.error(e)
            return JsonResponse({"code": RETCODE.DBERR, "errmsg": "新增地址失败"})

        # 若新增地址成功，将新增地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email,

        }
        logger.info(address_dict)
        # 响应保存结果
        return JsonResponse({"code": RETCODE.OK, "errmsg": "新增地址成功", "address": address_dict})

    # class AddressView(Lr):
    """"""


class UpdataDestroyAddressVIew(Lr):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""

        # 获取json字典
        json_dict = json.loads(request.body.decode())

        # 取出各字段信息
        title = json_dict.get("title")
        receiver = json_dict.get("receiver")
        province_id = json_dict.get("province_id")
        city_id = json_dict.get("city_id")
        district_id = json_dict.get("district_id")
        place = json_dict.get("place")
        mobile = json_dict.get("mobile")
        tel = json_dict.get("tel")
        email = json_dict.get("email")

        # 校验参数
        if not all([title, receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden("缺少必传参数")
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            return HttpResponseForbidden("号码错误")
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r"^[a-z0-9][\w\.\_]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
                return HttpResponseForbidden("邮箱格式错误")

                # 保存地址信息

        # 看能否更新数据  不能就是数据库问题
        try:
            address = Address.objects.filter(id=address_id).update(
                user=request.user,
                title=title,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

        except Exception as e:
            logger.error(e)

            return JsonResponse({"code": RETCODE.DBERR, "errmsg": "修改失败"})

        # 获取id 所对应地址对象
        address = Address.objects.get(id=address_id)

        # 构建成字典
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        print(address_dict)
        return JsonResponse({"code": RETCODE.OK, "errmsg": "修改成功", "address": address_dict})

    def delete(self, request, address_id):
        """删除地址"""

        try:
            # get请求查不到  会报错
            address = Address.objects.get(id=address_id)

            # 逻辑删除
            address.is_deleted = True
            # 数据库保存
            address.save()

        except Exception as e:
            logger.error("1", e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除成功'})


class DefaultAddressView(Lr):
    """设置默认地址"""

    def put(self, request, address_id):

        # 获取前端传入地址id  若不正确会报错
        try:
            address = Address.objects.get(id=address_id)

            # 设置成默认
            request.user.default_address = address

            # 保存
            request.user.save()
        except Exception as e:
            logger.error(e)

            return JsonResponse({"code": RETCODE.DBERR, "errmsg": "设置失败"})
        return JsonResponse({"code": RETCODE.OK, "errmsg": "设置成功"})


class UpdateTitleView(Lr):
    """修改用户收货地址标题"""

    def put(self, request, address_id):

        # 得到json字典 并解析
        json_dict = json.loads(request.body.decode())

        # 取出title
        title = json_dict.get("title")

        # 判断title是否存在
        if title is None:
            return JsonResponse({"code": RETCODE.PARAMERR, "errmsg": '缺少参数'})

        try:
            # 根据id获取地址对象
            address = Address.objects.get(id=address_id)

            # 更改标题并保存
            address.title = title
            address.save()

        except Exception as e:

            logger.error(e)
            # 响应结果
            return JsonResponse({"code": RETCODE.DBERR, "errmsg": '修改失败'})

        return JsonResponse({"code": RETCODE.OK, "errmsg": '修改成功'})


class ChangePasswordView(Lr):
    """修改密码视图"""

    def get(self, request):
        # 渲染出密码修改视图
        return render(request, "user_center_pass.html")

    def post(self, request):
        # 获取参数  旧密码  新密码  新密码2
        password_old = request.POST.get("old_pwd")
        password_new = request.POST.get("new_pwd")
        password_new2 = request.POST.get("new_cpwd")

        # 检查是否所有参数齐全
        if all([password_old, password_new, password_new2]) is False:
            return HttpResponseForbidden("参数不齐")
        # 检查旧密码
        if request.user.check_password(password_old) is False:
            return render(request, "user_center_pass.html", {"origin_pwd_errmsg": "原始密码不对"})
        # 检查新密码
        if not re.match(r"^[0-9A-Za-z]{8,20}$", password_new):
            return HttpResponseForbidden("格式不对")

        # 检查两次密码是否一致
        if password_new != password_new2:
            return HttpResponseForbidden("密码不一致")

        # 校验完毕  保存至数据库
        try:
            request.user.set_password(password_new)
            request.user.save()

        except Exception as e:

            return render(request, "user_center_pass.html", {"change_pwd_errmsg": "修改密码失败"})

        # 清理状态保持
        logout(request)
        # 重定向到登录页面
        # response = redirect("/login/")
        response = redirect(reverse('users:login'))
        # 删除cookie
        response.delete_cookie("username")

        return response


class UserBrowseHistory(Lr):
    """用户浏览记录"""

    def post(self, request):

        # 接收数据
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get("sku_id")
        # 检验数据有效性
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden("sku_id不存在")

        # 创建redis连接对象
        redis_conn = get_redis_connection("history")
        p1 = redis_conn.pipeline()
        # 获取用户对象
        user = request.user
        # 构建redis 的 key
        key = "history_%s" % user
        # 去重
        # redis_conn.lrem(key, 0, sku_id)
        p1.lrem(key, 0, sku_id)
        # 重置到开头
        # redis_conn.lpush(key, sku_id)
        p1.lpush(key, sku_id)
        # 截取
        # redis_conn.ltrim(key, 0, 4)
        p1.ltrim(key, 0, 4)

        # 执行管道
        p1.execute()

        return JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})

    def get(self, request):
        """展示浏览记录"""

        # 获取redis中的列表
        redis_conn = get_redis_connection("history")
        sku_id_ls = redis_conn.lrange(("history_%s") % request.user, 0, -1)

        # 构建控列表
        skus = []

        for sku_id in sku_id_ls:
            # 获取商品对象
            sku = SKU.objects.get(id=sku_id)
            # 列表加字典
            skus.append({
                "id": sku.id,
                "name": sku.name,
                "default_image_url": sku.default_image.url,
                "price": sku.price
            })

        # 响应结果
        return JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "skus": skus})


class FindPassWordView(View):
    """找回密码视图"""

    def get(self, request):
        return render(request, "find_password.html")


class AccountsView(View):
    """输入账户名 验证"""

    def get(self, request, username):

        # 根据mobile查询数据库
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseForbidden("用户不存在")

        # 提取验证码
        text = request.GET.get("text")
        image_code_id = request.GET.get("image_code_id")

        if all([text, image_code_id]) is False:
            return HttpResponseForbidden("参数不齐")

        # 校验验证码
        redis_conn = get_redis_connection("verify_code")
        image_code_server = redis_conn.get("img_%s" % image_code_id).decode()

        # 判断是否过期
        if image_code_server is None:
            return JsonResponse({"code": 400, "errmsg": "error"}, status=400)

        # 判断图型验证码是否一致
        print(image_code_server, text)
        if image_code_server.lower() != text.lower():
            return JsonResponse({"code": 400, "errmsg": "error"}, status=400)

        # 获取手机号
        mobile = user.mobile

        # 加密username作为access_token
        access_token = generat_openid_signature(mobile)

        return JsonResponse({"code": RETCODE.OK, "errmsg": "Ok", "mobile": mobile, "access_token": access_token})


class SendSMSView(View):
    """发送短信验证码"""

    def get(self, request):
        access_token = request.GET.get("access_token")

        mobile = check_openid_signature(access_token)

        sms_code = "%06d" % random.randint(0, 999999)
        print(mobile, sms_code)
        logger.info(sms_code, "jafjsdkajfk")
        # 调用发短信
        ccp_send_sms_code.delay(mobile, sms_code)
        # 存入redis
        redis_coon = get_redis_connection("verify_code")
        redis_coon.setex("sms_code_%s" % mobile, 60, sms_code)
        # 响应结果
        return JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})


class CheckSMSView(View):
    """检验短信验证码"""

    def get(self, request, username):

        print(username)
        try:
            # 根据username取出user
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseForbidden("用户不存在")

        # 取出验证码
        sms_code_client = request.GET.get("sms_code")
        # 取出redis中的验证码
        redis_coon = get_redis_connection("verify_code")
        try:
            sms_code_server = redis_coon.get("sms_code_%s" % user.mobile).decode()
        except Exception as e:
            return JsonResponse({"status": 404, "error_sms_code_message": "手机号不存在"})
        print(sms_code_server,sms_code_client)
        if sms_code_client.lower() != sms_code_server.lower():
            return JsonResponse({"status": 400, "error_sms_code_message": "验证码错误"})
        print("efrshgtfshyfjngedhjd")
        # 加密username作为access_token
        access_token = generat_openid_signature(user.mobile)
        print("xxx")
        # 响应数据
        # data = {
        #     "user_id": user.id,
        #     "access_token": access_token
        # }
        # return JsonResponse({"code": RETCODE.OK, "errmsg": "ok", "data": data})
        return JsonResponse({"code": RETCODE.OK, "errmsg": "ok", "user_id": user.id,"access_token": access_token})


class CheckWordView(View):
    """核对密码"""

    def post(self, request, user_id):

        # 取出user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponseForbidden("用户不存在")
        # 取出密码
        data_dict = json.loads(request.body.decode())
        password = data_dict.get("password", "")
        password2 = data_dict.get("password2", "")
        access_token = data_dict.get("access_token", "")

        # 校验参数
        if not all([password, password2, access_token]):
            return HttpResponseForbidden("参数不齐")

        mobile = check_openid_signature(access_token)
        if mobile != user.mobile:
            return HttpResponseForbidden("身份过期")

        if (len(password) < 8) or (len(password) > 20):
            return HttpResponseForbidden("密码长度不对")

        if password != password2:
            return HttpResponseForbidden("密码不一致")
        print("fhdoijregjvdfasgkjsije")
        # 校验完毕  保存至数据库
        try:
            user.set_password(password)
            user.save()

        except Exception as e:

            return JsonResponse({"error":"数据错误"},status=400)


        return JsonResponse({"message":"ok"})
