# ==========================
# User and Role Models / 用户与角色模型
# ==========================
# 该模块定义了自定义用户模型、角色模型和权限模型，
# 主要用于实现基于角色的访问控制 (RBAC)。

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    自定义用户模型，继承自 Django 的 AbstractUser。
    可在此扩展用户相关的字段和方法。
    """
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="用户的电话号码")
    address = models.CharField(max_length=255, blank=True, null=True, help_text="用户的地址")
    name = models.CharField(max_length=255, blank=False, null=True, help_text="用户的姓名")

class Role(models.Model):
    """
    角色模型：用于定义系统中的不同角色。
    """
    name = models.CharField(max_length=50, unique=True, help_text="角色名称，唯一标识")
    description = models.TextField(blank=True, help_text="角色描述")
    created_at = models.DateTimeField(auto_now_add=True, help_text="角色创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="角色更新时间")

    def __str__(self):
        return self.name

# ==========================
# Permission Models / 权限模型
# ==========================
# 该模块定义权限模型，用于支持更细粒度的访问控制。

class Permission(models.Model):
    """
    权限模型：用于定义系统中的操作权限。
    """
    name = models.CharField(max_length=50, unique=True, help_text="权限名称，唯一标识")
    codename = models.CharField(max_length=100, unique=True, help_text="权限的代码标识，用于程序调用")
    parent_id = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name='children',
        help_text="父级权限，用于权限的分层管理"
    )

    def __str__(self):
        return self.name

# ==========================
# Relationship Models / 关系模型
# ==========================
# 该模块定义用户-角色、角色-权限的多对多关系。

class UserRole(models.Model):
    """
    用户与角色的关系表：用于表示用户拥有哪些角色。
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_roles",
        help_text="关联的用户"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_users",
        help_text="关联的角色"
    )

    class Meta:
        unique_together = ('user', 'role')
        verbose_name = "用户角色关系"
        verbose_name_plural = "用户角色关系"

class RolePermission(models.Model):
    """
    角色与权限的关系表：用于表示角色拥有哪些权限。
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
        help_text="关联的角色"
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="permission_roles",
        help_text="关联的权限"
    )

    class Meta:
        unique_together = ('role', 'permission')
        verbose_name = "角色权限关系"
        verbose_name_plural = "角色权限关系"
