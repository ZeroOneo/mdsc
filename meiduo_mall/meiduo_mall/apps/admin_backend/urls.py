from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from admin_backend.views.login import UserLoginView

urlpatterns = [

   # 原始方法
   # url(r'^meiduo_admin/authorizations/$', UserLoginView.as_view())


   # 流弊方法   obtain_jwt_token 只返回token  需要重写 JWT_RESPONSE_PAYLOAD_HANDLER
   url(r'^meiduo_admin/authorizations/$', obtain_jwt_token)

]
