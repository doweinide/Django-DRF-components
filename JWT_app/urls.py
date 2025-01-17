from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserLoginView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 获取访问令牌
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 刷新令牌
    path('login/', UserLoginView.as_view(), name='user_login'),  # 用户登录
]
