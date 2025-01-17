from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import authenticate_user, generate_tokens_for_user

class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        # 获取请求中的用户账号和密码
        username = request.data.get('username')
        password = request.data.get('password')

        # 验证用户
        user = authenticate_user(username, password)
        if user is not None:
            # 生成 token
            access_token, refresh_token = generate_tokens_for_user(user)
            return Response({
                'access': access_token,
                'refresh': refresh_token
            })
        return Response({
            'detail': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
