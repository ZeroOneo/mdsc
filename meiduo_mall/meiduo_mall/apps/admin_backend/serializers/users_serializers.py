from rest_framework import serializers

from users.models import User


class ShowUsersModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "mobile", "email"]
        # fields = ["id", "username", "mobile", "email", "password"]

    #     # {
    #     #     "id": "用户id",
    #     #     "username": "用户名",
    #     #     "mobile": "手机号",
    #     #     "email": "邮箱"
    #     # }
    #     extra_kwargs = {
    #         "id": {"read_only": True},
    #         "password": {"write_only": True}
    #     }
    #
    # def create(self, validated_data):
    #     print(validated_data)
    #     # # 取出密码
    #     password = validated_data["password"]
    #     print(password)
    #     # # 加密
    #     # validated_data["password"] = make_password(password)
    #     #
    #     # # 附权限
    #     # validated_data["is_staff"] = True
    #     #
    #     # # 响应返回
    #     # return self.Meta.model.objects.create(**validated_data)
    #
    #     return self.Meta.model.objects.create_superuser(**validated_data)
