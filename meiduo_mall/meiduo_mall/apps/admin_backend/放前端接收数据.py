# 3、获取SPU商品规格信息
# 接口分析
# 请求方式： GET meiduo_admin/goods/(?P<pk>\d+)/specs/
#
# 请求参数： 通过请求头传递jwt token数据。
#
# 在路径中传递当前SPU商品id
#
# 返回数据： JSON
#
#  [
#         {
#             "id": "规格id",
#             "name": "规格名称",
#             "spu": "SPU商品名称",
#             "spu_id": "SPU商品id",
#             "options": [
#                 {
#                     "id": "选项id",
#                     "name": "选项名称"
#                 },
#                 ...