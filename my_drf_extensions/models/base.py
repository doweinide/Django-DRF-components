from django.db import models

class BaseModel(models.Model):
    """
    一个通用的基础模型，包含一些公共字段。
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
