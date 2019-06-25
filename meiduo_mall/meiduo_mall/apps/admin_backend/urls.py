from django.conf.urls import url
from rest_framework.routers import SimpleRouter
from rest_framework_jwt.views import obtain_jwt_token

from admin_backend.views.channel_view import GoodsChannelsView
from admin_backend.views.sku_view import *
from admin_backend.views.home_view import *
from admin_backend.views.specs_options_view import *
from admin_backend.views.specs_view import SpecsModelViewSet
from admin_backend.views.spu_view import *
from admin_backend.views.users_view import *
from admin_backend.views.goodsBrands_view import GoodBrandsModelViewSet

urlpatterns = [

    # 原始方法
    # url(r'^authorizations/$', UserLoginView.as_view())

    # 流弊方法   obtain_jwt_token 只返回token  需要重写 JWT_RESPONSE_PAYLOAD_HANDLER
    url(r'^authorizations/$', obtain_jwt_token),

    # # 原始方法
    # url(r'^statistical/total_count/$', HomeView.as_view())

    # 管理员用户新增和展示
    url(r"^users/$", UserView.as_view()),

    # SKU管理展示
    url(r"^skus/$", SkusModelView.as_view({"get": "list", "post": "create"})),

    # SKU管理删除
    url(r"^skus/(?P<pk>\d+)/$", SkusModelView.as_view({"delete": "destroy", "put": "update", "get": "retrieve"})),

    # 展示商品分类
    url(r"^skus/categories/$", CategoryView.as_view()),

    # SPU商品名称
    url(r"^goods/simple/$", SimpleView.as_view()),

    # SPU商品规格名称
    url(r"^goods/(?P<pk>\d+)/specs/$", SpecsView.as_view()),

    # SPU表展示,新增
    url(r"^goods/$", SPUModelViewset.as_view({"get": "list", "post": "create"})),

    # SPU表删除
    url(r"^goods/(?P<pk>\d+)/$", SPUModelViewset.as_view({"delete": "destroy", "put": 'update', "get": "retrieve"})),

    # SPU表新增---选择品牌
    url(r"^goods/brands/simple/$", SPUsimpleView.as_view()),

    # SPU表新增---显示一级类别
    url(r"^goods/channel/categories/$", SPUChannelView.as_view()),

    # SPU表新增---显示二、三级类别
    url(r"^goods/channel/categories/(?P<pk>\d+)/$", SPUchannel_23_View.as_view()),

    # 商品规格管理--展示  新增
    url(r"^goods/specs/$", SpecsModelViewSet.as_view({"get": "list", "post": "create"})),

    # 商品规格管理--修改
    url(r"^goods/specs/(?P<pk>\d+)/$",
        SpecsModelViewSet.as_view({"put": "update", "delete": "destroy", "get": "retrieve"})),

    # 商品规格选项管理--展示，新增
    url(r"^specs/options/$", SpecsOptionModelViewSet.as_view({"get": "list", "post": "create"})),

    # 商品规格选项管理--修改，删除
    url(r"^specs/options/(?P<pk>\d+)/$",
        SpecsOptionModelViewSet.as_view({"put": "update", "delete": "destroy", "get": "retrieve"})),

    # 商品规格选项管理--新增展示spu名
    url(r"^goods/specs/simple/$", SpecsSimpleView.as_view()),

    # 商品规格选项管理--修改
    url(r"^goods/specs/simple/(?P<pk>\d+)/$", SpecsSimpleUpadateView.as_view()),

    # 商品頻道管理--展示所有信息---新建
    url(r"^goods/channels/$", GoodsChannelsView.as_view({"get": "list", "post": "create"})),

    # 商品頻道管理--修改--展示单条信息
    url(r"^goods/channels/(?P<pk>\d+)/$",
        GoodsChannelsView.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),

    # 商品頻道管理--展示頻道分組
    url(r"^goods/channel_types/$", GoodsChannelsView.as_view({"get": "channel_types"})),

    # 商品頻道管理--展示一級分類
    url(r"^goods/categories/$", GoodsChannelsView.as_view({"get": "categories"})),

    # 商品品牌管理--展示所有信息
    url(r"^goods/brands/$", GoodBrandsModelViewSet.as_view({"get": "list"})),

]

# ----------------------------------------------------------------------------------------------
# WARNING basehttp 124 "GET /meiduo_admin/statistical/total_count/ HTTP/1.1" 404 9871

# 获取对象
router = SimpleRouter()

# 注册路由
router.register(prefix="statistical", viewset=HomeViewSet, basename="首页")

# 添加路由
urlpatterns += router.urls
# -----------------------------------------------------------------------------------------------
