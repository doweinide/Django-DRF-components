# rbac/serializers.py


from rest_framework import serializers
from .models import Role, Permission, UserRole, RolePermission, CustomUser

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()  # 动态获取用户模型

# 权限 序列化器
class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'password','name','email', 'phone_number', 'address','last_login','date_joined','is_active']  # 包括所有需要的字段
        # fields = '__all__'
    def create(self, validated_data):
        # 从数据中移除密码并加密后保存用户
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # 使用 set_password 方法加密密码
        user.save()
        return user

    def update(self, instance, validated_data):
        # 更新密码时确保加密
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


# 角色 序列化器
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

# 权限  菜单  序列化器
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

# 用户角色关系 序列化器
class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role']

# 角色权限关系 序列化器
class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'permission']

# User serializer with role selection
class UserSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        write_only=True
    )

    class Meta:
        model = CustomUser

        fields = ['id', 'username', 'email', 'password', 'roles']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        # Assign roles to user
        for role in roles:
            UserRole.objects.create(user=user, role=role)
        return user

    def update(self, instance, validated_data):
        roles = validated_data.pop('roles', [])
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()

        # Update roles
        UserRole.objects.filter(user=instance).delete()
        for role in roles:
            UserRole.objects.create(user=instance, role=role)
        return instance