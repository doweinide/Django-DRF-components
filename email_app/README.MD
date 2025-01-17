# 移植前置条件
使用 Celery异步发送邮件，需要在虚拟环境中安装 Celery 并正确运行 Celery 的任务和 Worker。以下是具体步骤：

---

## 一、安装 Celery 和 Redis
在你的虚拟环境中安装 Celery 和 Redis 的 Python 客户端：

```bash
pip install celery[redis]
```

- `celery[redis]` 安装 Celery 和 Redis 的依赖。
- 如果你还没有安装 Redis，可以在本地安装 Redis 服务器，或者使用 Docker 快速启动 Redis。

---

## 二、创建 Celery 配置和实例
在你的 Django 项目中，创建一个单独的文件 `celery.py` 来初始化 Celery。例如：

**项目结构：**
```
project_name/
    ├── project_name/
    │   ├── __init__.py
    │   ├── celery.py    # Celery 配置文件
    │   ├── settings.py
    │   └── ...
    ├── app_name/
    │   ├── tasks.py     # 定义 Celery 任务
    │   └── ...
```

**1. 配置 Celery（`celery.py`）：**

在你的项目主目录（与 `settings.py` 同级）下，创建一个 `celery.py` 文件：

```python
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置 Django 默认配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

# 创建 Celery 应用
app = Celery('project_name')

# 从 Django 的 settings.py 加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务 (tasks.py)
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

**2. 修改 `__init__.py`：**

确保在 Django 项目的 `__init__.py` 中加载 Celery 应用：

```python
from __future__ import absolute_import, unicode_literals

# 使得 celery 应用可以随项目启动
from .celery import app as celery_app

__all__ = ('celery_app',)
```

---

## 三、定义任务
在每个需要用到 Celery 的应用中，创建 `tasks.py` 文件。

例如，在 `app_name` 应用的 `tasks.py` 中定义一个简单任务：

```python
from celery import shared_task

@shared_task
def add(x, y):
    return x + y
```

---

## 四、启动 Celery Worker
在终端中运行 Celery Worker，用于执行任务。

```bash
celery -A project_name worker --loglevel=info
```

- `-A project_name` 指定你的 Django 项目名称。
- `worker` 启动任务 Worker。
- `--loglevel=info` 查看详细日志。

---

## 五、运行 Redis
确保 Redis 服务正常运行。如果未安装 Redis，可以使用 Docker 快速启动：

```bash
docker run -d -p 6379:6379 redis
```

---

## 六、测试任务
在 Django Shell 中调用任务：

```bash
python manage.py shell
```

执行任务：

```python
from app_name.tasks import add
result = add.delay(4, 6)
print(result.get())  # 输出：10
```

---

## 七、是否需要单独运行？
- **是的，需要单独运行 Celery Worker 和 Redis 服务**：
  - Redis 是 Celery 的消息中间件，需要单独启动。
  - Celery Worker 用于执行任务，也需要单独运行。

---

### 最终总结
1. **Redis**：作为消息队列，必须运行。
2. **Celery Worker**：处理任务，必须单独启动。
3. **Django 应用**：正常运行即可调用 Celery 的任务。

完整流程：启动 Redis → 启动 Celery Worker → 测试任务。