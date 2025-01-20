## 一、Django 实现 SSE 的固定操作

### （一）避免跨域问题

1. 安装 `django-cors-headers` 库
   - 通过以下命令安装跨域处理库：
     ```bash
     pip install django-cors-headers
     ```

2. 配置 `ALLOWED_HOSTS` 和 `CORS_ALLOWED_ORIGINS`
   - 在 `settings.py` 中设置允许访问的主机和允许的跨域请求源：
     ```python
     ALLOWED_HOSTS = ['192.168.1.9', '127.0.0.1', 'http://localhost:5778']

     CORS_ALLOWED_ORIGINS = [
         'http://localhost:5778',  # 允许的域名
         'http://127.0.0.1',
         'http://192.168.1.9',     # 另一个允许的域名
     ]
     ```

3. 启用 `django-cors-headers`
   - 在 `INSTALLED_APPS` 中添加 `corsheaders`：
     ```python
     INSTALLED_APPS = [
         'corsheaders',  # 跨域问题处理
     ]
     ```

4. 配置中间件
   - 在 `MIDDLEWARE` 中添加 `CorsMiddleware`，用于处理跨域问题：
     ```python
     MIDDLEWARE = [
         'corsheaders.middleware.CorsMiddleware',  # 处理跨域请求
         'django.middleware.common.CommonMiddleware',
     ]
     ```

### （二）配置异步服务器支持 SSE

1. 安装 `daphne` 作为异步服务器
   - 通过以下命令安装 `daphne`：
     ```bash
     pip install daphne
     ```

2. 配置 `ASGI_APPLICATION`
   - 在 `settings.py` 中指定 ASGI 应用：
     ```python
     ASGI_APPLICATION = "DRF_useful_components.asgi.application"
     ```

3. 启用 `daphne` 应用
   - 在 `INSTALLED_APPS` 中添加 `daphne`：
     ```python
     INSTALLED_APPS = [
         'daphne',  # 异步（SSE等）支持
     ]
     ```

### （三）使用 `StreamingHttpResponse` 实现 SSE

1. 在 `views.py` 中使用 `StreamingHttpResponse` 来处理 SSE 请求，确保服务端能持续向客户端推送数据流：
   ```python
   from django.http import StreamingHttpResponse
   import time

   def event_stream():
       while True:
           yield f"data: {time.time()}\n\n"
           time.sleep(1)

   def sse_view(request):
       return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
   ```

通过以上步骤，您可以在 Django 中成功配置并实现 SSE（Server-Sent Events），并且避免跨域问题。