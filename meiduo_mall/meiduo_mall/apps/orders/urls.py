from django.conf.urls import url
from . import views

urlpatterns = [
    # 订单页面视图
    url(r'orders/settlement/$', views.OrderSettlementView.as_view()),
    # 提交订单页面视图
    url(r'orders/commit/$', views.OrderCommitView.as_view()),
    # 提交订单页面视图
    url(r'orders/success/$', views.OrderSuccessView.as_view()),
    # 显示订单页面视图
    url(r'orders/info/(?P<page_num>\d+)/$', views.OrderShowView.as_view()),

]
