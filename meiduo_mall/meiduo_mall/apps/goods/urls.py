from django.conf.urls import url
from . import views

urlpatterns = [
    # 商品列表
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view()),
    # 热销商品
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
    # 商品详情
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view()),
    # 商品访问量路由
    url(r'^visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view()),

]
