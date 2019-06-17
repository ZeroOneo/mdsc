from django.conf.urls import url

from . import views

urlpatterns = [
    # qq登陆界面路由
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    # QQ登陆后的回调处理
    url(r'^oauth_callback/$', views.QQAuthView.as_view()),
    # wb请求url
    url(r'^sina/login/$', views.WBAuthURLView.as_view()),
    # wb返回url
    url(r'^sina_callback/$', views.WBCallBackView.as_view()),
    # wb返回url
    url(r'^oauth/sina/user/$', views.WBUserView.as_view()),
]
