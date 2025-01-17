# myproject/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置默认的 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DRF_useFul_Components.settings')

# 创建一个 Celery 实例
app = Celery('DRF_useFul_Components')

# 使用字符串形式配置 Celery，'CELERY_BROKER_URL' 指定了消息代理
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()
