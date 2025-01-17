# rbac/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, PermissionViewSet, UserRoleViewSet, RolePermissionViewSet, UserPermissionsViewSet, \
    AllUsersPermissionsViewSet, UserManagementViewSet, CustomUserViewSet, LoginView, UserInfoView, UserMenuView, \
    MenuToPermissionAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'role-permissions', RolePermissionViewSet)

#查询
router.register(r'user-permissions', UserPermissionsViewSet, basename='user-permissions')
router.register(r'all-users-permissions', AllUsersPermissionsViewSet, basename='all-users-permissions')
router.register(r'all-users', UserManagementViewSet, basename='user-management')
urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 获取访问令牌
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 刷新令牌
    path('login', LoginView.as_view(), name='login'),
    path('userInfo', UserInfoView.as_view(), name='userInfo'),
    path('menu', UserMenuView.as_view(), name='userMenu'),
    path('menu-to-permission/', MenuToPermissionAPIView.as_view(), name='menu-to-permission-api'),

]
