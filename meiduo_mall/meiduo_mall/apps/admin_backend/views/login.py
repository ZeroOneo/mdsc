from rest_framework.views import APIView
from admin_backend.serializers.login_serializers import LoginSerializer
from rest_framework.response import Response

class UserLoginView(APIView):
    """后台站点登陆"""

    def post(self,request):

        # 进行身份认证
        serializer = LoginSerializer(data=request.data)

        # 校验
        serializer.is_valid(raise_exception=True)

        # 响应
        return Response({
            "username":serializer.validated_data.get("user").username,
            "user_id":serializer.validated_data.get("user").id,
            "token":serializer.validated_data.get("jwt_token")
        })