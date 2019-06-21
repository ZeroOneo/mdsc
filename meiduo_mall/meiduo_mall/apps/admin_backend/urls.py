from django.conf.urls import url
from rest_framework.routers import SimpleRouter
from rest_framework_jwt.views import obtain_jwt_token
from admin_backend.views.users import *
from admin_backend.views.home import *

urlpatterns = [

    # 原始方法
    # url(r'^meiduo_admin/authorizations/$', UserLoginView.as_view())

    # 流弊方法   obtain_jwt_token 只返回token  需要重写 JWT_RESPONSE_PAYLOAD_HANDLER
    url(r'^meiduo_admin/authorizations/$', obtain_jwt_token),

    # # 原始方法
    # url(r'^meiduo_admin/statistical/total_count/$', HomeView.as_view())

    url(r"^meiduo_admin/users/$",UserView.as_view())
]


# ----------------------------------------------------------------------------------------------
# WARNING basehttp 124 "GET /meiduo_admin/statistical/total_count/ HTTP/1.1" 404 9871

# 获取对象
router = SimpleRouter()

# 注册路由
router.register(prefix="meiduo_admin/statistical", viewset=HomeViewSet, basename="首页")

# 添加路由
urlpatterns += router.urls
# -----------------------------------------------------------------------------------------------