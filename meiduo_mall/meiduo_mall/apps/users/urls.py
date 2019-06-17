"""mdsc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    # 注册页面路由
    url(r'^register/', views.RegisterView.as_view(), name='register'),
    # 验证重名路由
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/', views.UserCountView.as_view(), name='usernames'),
    # 验证手机号重复
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/', views.MobileCountView.as_view(), name='mobiles'),
    # 登录验证
    url(r'^login/', views.LoginView.as_view(), name='login'),
    # 登出验证
    url(r'^logout/', views.LogoutView.as_view(), name='logout'),
    # 用户中心视图
    url(r'^info/', views.UserInfoView.as_view(), name='info'),
    # 发送ｅｍａｉｌ视图
    url(r'^emails/$', views.EmailView.as_view(), name='emails'),
    # 核查ｅｍａｉｌ
    url(r'^emails/verification/$', views.VerifyEmailView.as_view(), name="verifyemails"),
    # 收货地址路由
    url(r'^addresses/$', views.AddressView.as_view(), name="address"),
    # 收货地址路由
    url(r'^addresses/create/$', views.CreateAddressVIew.as_view(), name="create"),
    # 收货地址路由
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdataDestroyAddressVIew.as_view(), name="addresses_d"),
    # 默认地址路由
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(), name="default_ad"),
    # 修改地址标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleView.as_view(), name="title"),
    # 修改密码
    url(r'^password/$', views.ChangePasswordView.as_view(), name="password"),
    # 浏览记录
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view(), name="browse_histories"),
    # 找回密码0
    url(r'^find_password/$', views.FindPassWordView.as_view()),
    # 找回密码1
    url(r'^accounts/(?P<username>[a-zA-Z0-9-_]{5,20})/sms/token/$', views.AccountsView.as_view()),
    # 找回密码2
    url(r'^sms_codes/$', views.SendSMSView.as_view()),
    # 找回密码3
    url(r'^accounts/(?P<username>[a-zA-Z0-9_]{5,20})/password/token/$', views.CheckSMSView.as_view()),
    # 找回密码4
    url(r'^users/(?P<user_id>\d+)/password/$', views.CheckWordView.as_view()),
]
