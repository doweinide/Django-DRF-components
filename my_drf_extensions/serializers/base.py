from rest_framework import serializers

class BaseSerializer(serializers.ModelSerializer):
    """
    一个基础的序列化器，扩展了默认功能。
    """
    def validate(self, attrs):
        # 自定义验证逻辑
        return super().validate(attrs)
