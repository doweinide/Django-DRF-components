from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

def authenticate_user(username, password):
    """
    验证用户名和密码是否正确
    :param username: 用户名
    :param password: 密码
    :return: 返回用户对象，如果验证失败返回 None
    """
    user = authenticate(username=username, password=password)
    return user

def generate_tokens_for_user(user):
    """
    生成 access token 和 refresh token
    :param user: 用户对象
    :return: 返回 access token 和 refresh token
    """
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    return access_token, refresh_token
