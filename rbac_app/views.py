# rbac/views.py
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db.models import Q, Count
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from self_drf_extensions.views import SearchableListModelMixin
from .models import Role, Permission, UserRole, RolePermission,CustomUser
from .serializers import RoleSerializer, PermissionSerializer, UserRoleSerializer, RolePermissionSerializer, \
    UserSerializer, CustomUserSerializer
User = CustomUser

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes=[AllowAny]

#token生成， 登录接口
def generate_login_response(user):
    """
    生成登录成功后的响应数据，包括令牌、角色和权限信息。
    """
    # 生成 refresh 和 access 令牌
    refresh = RefreshToken.for_user(user)

    # 获取用户的角色
    roles = UserRole.objects.filter(user=user).values_list('role', flat=True)
    # 获取用户的角色名称
    roles_names = UserRole.objects.filter(user=user).select_related('role').values_list('role__name', flat=True)

    # 将角色名称转换为列表
    roles_list = list(roles_names)

    # 获取这些角色对应的权限
    permissions = RolePermission.objects.filter(role__in=roles).values(
        'permission__id',
        'permission__name',
        'permission__codename',
        'permission__parent_id',
        'role__name'  # 添加 parent_id
    ).distinct()

    # 格式化权限信息
    permissions_data = {
        'role_name': roles_list,
        'menu': list(permissions)
    }

    return {
        'refresh': str(refresh),
        'accessToken': str(refresh.access_token),
        'username': user.username,
        'permissions': permissions_data
    }


class LoginView(APIView):
    permission_classes = [AllowAny]  # 不需要身份验证

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)  # 这里会自动更新 last_login

            # 调用提取的函数来生成响应数据
            response_data = generate_login_response(user)

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
# 用户信息
class UserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user_info = {
            'realName':user.name,
            'username': user.username,
            'email': user.email,
            # 其他需要返回的用户信息
        }
        return Response(user_info)

# 用户角色的菜单
class UserMenuView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 获取用户的角色
        roles = UserRole.objects.filter(user=user).values_list('role', flat=True)
        # 获取用户的角色名称
        roles_names = UserRole.objects.filter(user=user).select_related('role').values_list('role__name', flat=True)

        # 将查询结果转换为列表
        roles_list = list(roles_names)
        # 获取这些角色对应的权限
        permissions = RolePermission.objects.filter(role__in=roles).values(
            'permission__id',
            'permission__name',
            'permission__codename',
            'permission__parent_id',
            'role__name'  # 添加 parent_id
        ).distinct()


        return Response({
            'roles': roles_list,
            'menu': list(permissions)
        })

# 更新菜单
class MenuToPermissionAPIView(APIView):
    def post(self, request):
        data = request.data

        # 开启事务
        with transaction.atomic():
            # 获取所有现有的权限，存储为字典 {name: Permission}
            existing_permissions = {perm.name: perm for perm in Permission.objects.all()}

            # 用于存储当前处理过的权限名
            processed_names = set()

            # 递归保存或更新菜单项为权限
            def save_or_update_permissions(menu_items, parent_permission=None):
                for item in menu_items:
                    name = item['name']  # 用 `name` 作为唯一标识
                    codename = name  # 假设 `codename` 可以用 `name` 代替

                    # 检查是否已经存在该权限
                    if name in existing_permissions:
                        # 权限已存在，跳过创建，但更新其父级并记录
                        permission = existing_permissions[name]
                        permission.parent_id = parent_permission
                        permission.save()
                        processed_names.add(name)
                    else:
                        # 创建新权限
                        permission = Permission.objects.create(
                            name=name,
                            codename=codename,
                            parent_id=parent_permission
                        )
                        # 添加到字典以防后续重复
                        existing_permissions[name] = permission
                        processed_names.add(name)

                    # 递归保存或更新子菜单项的权限
                    children = item.get('children', [])
                    if children:
                        save_or_update_permissions(children, parent_permission=permission)

            # 开始处理数据
            save_or_update_permissions(data)

            # 删除未处理的权限
            for name, permission in existing_permissions.items():
                if name not in processed_names:
                    permission.delete()

        return Response({"detail": "菜单数据已成功更新到权限表"}, status=status.HTTP_200_OK)

# 用户角色
class RoleViewSet(SearchableListModelMixin):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    time_range_fields = ['created_at', 'updated_at']

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = None  # 禁用分页器
    # permission_classes = [permissions.IsAdminUser]

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    # permission_classes = [permissions.IsAdminUser]

# 获取角色对应菜单
class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    pagination_class = None  # 禁用分页器
    # permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        role_id = request.data.get('role')
        permission = request.data.get('permission')
        permissions = request.data.get('permissions', [])

        # 检查是否提供了角色
        if not role_id:
            return Response(
                {"detail": "Role is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查角色是否存在
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {"detail": "Role not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 如果提供了单个 permission，验证并添加它
        if permission:
            try:
                valid_permission = Permission.objects.get(id=permission)
                # 检查角色当前是否已有该权限，避免重复添加
                if not RolePermission.objects.filter(role=role, permission=valid_permission).exists():
                    RolePermission.objects.create(role=role, permission=valid_permission)
                    return Response(
                        {"detail": "Permission successfully added to role."},
                        status=status.HTTP_201_CREATED
                    )
                else:
                    return Response(
                        {"detail": "Permission already exists for this role."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Permission.DoesNotExist:
                return Response(
                    {"detail": "Invalid permission."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 如果没有提供单个 permission，则检查 permissions 列表
        if permissions:
            return Response(
                {"detail": "Please provide only one permission."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 如果没有提供权限，则返回错误
        return Response(
            {"detail": "At least one permission is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 重写 retrieve 方法 获取角色的菜单
    def retrieve(self, request, pk=None, *args, **kwargs):
        # pk 实际上是 roles 的 id
        role_permissions = self.queryset.filter(role_id=pk)
        serializer = self.get_serializer(role_permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        role_id = request.data.get('role_id')  # 从请求中获取 role_id
        permissions = request.data.get('permissions', [])  # 获取权限列表 permissions[]

        # 检查是否提供了 role_id
        if not role_id:
            return Response(
                {"detail": "角色是必需的。"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查是否提供了权限列表
        if not permissions:
            return Response(
                {"detail": "至少需要一个权限。"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 根据 role_id 获取角色对象
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {"detail": "角色未找到。"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 处理提供的权限列表
        permission_ids = [perm.get('id') for perm in permissions]  # 提取权限 ID 列表

        # 验证权限是否存在
        valid_permissions = Permission.objects.filter(id__in=permission_ids)

        # 如果有无效的权限 ID，返回 400 错误
        if valid_permissions.count() != len(permission_ids):
            return Response(
                {"detail": "一个或多个权限无效。"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 在添加新权限之前，删除角色当前关联的所有权限
        RolePermission.objects.filter(role=role).delete()

        # 为角色创建新的权限关联
        for permission in valid_permissions:
            RolePermission.objects.create(role=role, permission=permission)

        return Response(
            {"detail": "角色的权限已成功更新。"},
            status=status.HTTP_200_OK
        )

class UserPermissionsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access

    def list(self, request):
        user = request.user
        # 获取用户的所有角色
        roles = UserRole.objects.filter(user=user).values_list('role', flat=True)

        # 获取这些角色对应的所有权限
        permissions = RolePermission.objects.filter(role__in=roles).values(
            'permission__id', 'permission__name', 'permission__codename'
        ).distinct()

        return Response(list(permissions))

# 用户权限视图集--前端 用户管理页面
class AllUsersPermissionsViewSet(viewsets.ModelViewSet):
    """
    AllUsersPermissionsViewSet 类
    ================================
    这是一个 Django ViewSet，用于处理用户的权限相关操作。

    属性:
        permission_classes: 设置视图的权限类（在此设置为允许所有用户访问）
        queryset: 定义视图查询的用户集合
        serializer_class: 指定用户的序列化类

    方法:
        list: 用于筛选和列出用户，根据传入的过滤条件返回符合条件的用户数据
        update: 更新指定用户的信息和角色
        create: 创建用户并分配角色
    """
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def list(self, request, *args, **kwargs):
        # 获取默认序列化器的字段
        serializer_fields = set(self.get_serializer().fields.keys())

        # 获取角色序列化器的字段
        role_serializer_fields = set(RoleSerializer().fields.keys())

        # 合并两个序列化器的字段集合
        all_fields = serializer_fields | role_serializer_fields

        # 构建查询集
        query = Q()
        query_params = self.request.query_params
        role_ids = query_params.getlist('roles[]')  # 获取 roles[] 参数

        # 处理 last_login 的时间范围过滤
        last_login_range = query_params.getlist('last_login[]')
        if last_login_range and len(last_login_range) == 2:
            start_date = parse_datetime(last_login_range[0])
            end_date = parse_datetime(last_login_range[1])
            if start_date and end_date:
                query.add(Q(last_login__range=(start_date, end_date)), Q.AND)

        # 处理 date_joined 的时间范围过滤
        date_joined_range = query_params.getlist('date_joined[]')
        if date_joined_range and len(date_joined_range) == 2:
            start_date = parse_datetime(date_joined_range[0])
            end_date = parse_datetime(date_joined_range[1])
            if start_date and end_date:
                query.add(Q(date_joined__range=(start_date, end_date)), Q.AND)

        # 处理其他查询参数
        for field, value in query_params.items():
            # 检查字段是否在序列化器字段集合中
            if field in all_fields and value:
                # 特殊处理布尔字段 is_active
                if field == 'is_active':
                    bool_value = value.lower() == 'true'
                    query.add(Q(**{f'{field}': bool_value}), Q.AND)
                elif field not in ['last_login[]', 'date_joined[]']:  # 跳过已处理的字段
                    query.add(Q(**{f'{field}__icontains': value}), Q.AND)

        # 如果提供了 role_ids，过滤拥有指定角色的用户；否则返回所有用户
        users = self.get_queryset().filter(query)
        if role_ids:
            users = users.filter(user_roles__role_id__in=role_ids) \
                .annotate(matching_roles=Count('user_roles__role_id', filter=Q(user_roles__role_id__in=role_ids))) \
                .filter(matching_roles=len(role_ids))  # 确保匹配角色数等于传入的角色 ID 数量

        # 分页
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            serialized_data = serializer.data
            # 获取角色 ID 和 name，并将其作为对象添加到用户数据中
            for user_data in serialized_data:
                roles = UserRole.objects.filter(user=user_data['id']).select_related('role').values('role__id',
                                                                                                    'role__name')
                user_data['roles'] = [{"id": role['role__id'], "name": role['role__name']} for role in roles]
            return self.get_paginated_response(serialized_data)

        # 直接序列化整个查询集
        serializer = self.get_serializer(users, many=True)
        serialized_data = serializer.data
        # 获取角色 ID 和 name，并将其作为对象添加到用户数据中
        for user_data in serialized_data:
            roles = UserRole.objects.filter(user=user_data['id']).select_related('role').values('role__id',
                                                                                                'role__name')
            user_data['roles'] = [{"id": role['role__id'], "name": role['role__name']} for role in roles]
        return Response(serialized_data)
    def update(self, request, pk=None, *args, **kwargs):
        # 获取当前用户对象
        user = self.get_object()

        # 处理序列化器，部分更新
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 更新用户的其他信息（由序列化器处理）
        updated_user = serializer.save()

        # 获取用户传入的角色数据
        roles_data = request.data.get('roles', [])

        # 获取当前用户的所有角色ID集合
        current_role_ids = UserRole.objects.filter(user=user).values_list('role_id', flat=True)

        # 获取所有可用的角色ID集合（基于提供的角色ID列表）
        available_roles = Role.objects.filter(id__in=roles_data).values_list('id', flat=True)

        # 构建要设置的角色ID集合
        roles_to_set = set(available_roles)

        # 找出要删除的角色ID（当前角色ID中不在新角色ID列表中的）
        roles_to_remove = set(current_role_ids) - roles_to_set

        # 删除不再需要的角色关联
        UserRole.objects.filter(user=user, role_id__in=roles_to_remove).delete()

        # 添加新的角色关联（确保不会重复添加）
        for role_id in roles_to_set:
            # 检查是否已经存在该用户和角色的关联
            if not UserRole.objects.filter(user=user, role_id=role_id).exists():
                UserRole.objects.create(user=user, role_id=role_id)

        # 返回更新成功的响应
        return Response({"status": "success", "detail": "User and roles updated successfully."},
                        status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # 创建用户
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 分配角色
        roles_data = request.data.get('roles', [])

        # 查找并分配对应角色ID的角色
        available_roles = Role.objects.filter(id__in=roles_data)

        # 遍历角色并创建关联
        for role in available_roles:
            UserRole.objects.create(user=user, role=role)

        return Response({"status": "success", "detail": "User created and roles assigned successfully."},
                        status=status.HTTP_201_CREATED)

class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAdminUser]  # Only admin users can access

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)