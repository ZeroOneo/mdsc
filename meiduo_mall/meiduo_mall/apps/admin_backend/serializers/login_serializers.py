from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler


class LoginSerializer(serializers.Serializer):
    # 定义校验字段
    username = serializers.CharField(max_length=20)
    password = serializers.CharField()

    def validate(self, attrs):
        # # 原始方法
        # username = attrs.get("username")
        # password = attrs.get("password")

        # 完成身份验证
        user = authenticate(**attrs)

        # 判断结果
        if not user:
            raise serializers.ValidationError("用户认证失败")

        # 认证成功 签发token
        payload = jwt_payload_handler(user)

        jwt_token = jwt_encode_handler(payload)

        # 返回
        return {
            "user": user,
            "jwt_token": jwt_token
        }
