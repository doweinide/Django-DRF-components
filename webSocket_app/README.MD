## 一、搭建 WebSocket Django 应用

### （一）准备工作

1. **安装必要的依赖**

   - 首先需要安装 `Django` 和 `Channels`。`Django Channels` 扩展库让 Django 支持 WebSocket 和其他异步协议。
   
   ```bash
   pip install django channels
   ```

2. **创建 Django 项目和应用**

   - 使用 `django-admin` 创建一个新的 Django 项目和一个应用。
   
   ```bash
   django-admin startproject myproject
   cd myproject
   python manage.py startapp chat
   ```

3. **安装 ASGI 服务器**

   - 由于 WebSocket 是基于异步的协议，Django 默认是基于 WSGI 的（即同步的），因此需要使用 ASGI 服务器来支持异步协议。
   - 安装 `daphne`，它是 Django Channels 推荐的 ASGI 服务器。

   ```bash
   pip install daphne
   ```

### （二）配置 Django Channels

1. **修改 `settings.py`**

   - 在 `INSTALLED_APPS` 中添加 `channels` 和 `chat` 应用。
   - 配置 `ASGI_APPLICATION` 为 `myproject.asgi.application`，指向 ASGI 配置文件。

   ```python
   INSTALLED_APPS = [
       ...
       'channels',
       'chat',
   ]

   ASGI_APPLICATION = 'myproject.asgi.application'
   ```

2. **创建 `asgi.py` 配置文件**

   - 在项目根目录下（与 `settings.py` 同级）创建 `asgi.py` 文件，并配置 Channels 路由。

   ```python
   import os
   from django.core.asgi import get_asgi_application
   from channels.routing import ProtocolTypeRouter, URLRouter
   from channels.auth import AuthMiddlewareStack
   from chat import routing

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

   application = ProtocolTypeRouter({
       "http": get_asgi_application(),
       "websocket": AuthMiddlewareStack(
           URLRouter(
               routing.websocket_urlpatterns
           )
       ),
   })
   ```

### （三）配置 WebSocket 路由

1. **创建 `routing.py`**

   - 在 `chat` 应用目录下创建 `routing.py` 文件，用于配置 WebSocket 路由。

   ```python
   from django.urls import re_path
   from . import consumers

   websocket_urlpatterns = [
       re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
   ]
   ```

### （四）编写 WebSocket 消费者

1. **创建消费者（Consumer）**

   - 消费者是 WebSocket 的核心，它负责接收来自客户端的消息、处理消息和发送消息回客户端。
   - 在 `chat` 应用中创建 `consumers.py` 文件，并定义一个简单的消费者类 `ChatConsumer`。

   ```python
   import json
   from channels.generic.websocket import AsyncWebsocketConsumer

   class ChatConsumer(AsyncWebsocketConsumer):
       async def connect(self):
           self.room_name = self.scope['url_route']['kwargs']['room_name']
           self.room_group_name = f'chat_{self.room_name}'

           # 加入房间组
           await self.channel_layer.group_add(
               self.room_group_name,
               self.channel_name
           )

           await self.accept()

       async def disconnect(self, close_code):
           # 离开房间组
           await self.channel_layer.group_discard(
               self.room_group_name,
               self.channel_name
           )

       # 接收来自 WebSocket 的消息
       async def receive(self, text_data):
           text_data_json = json.loads(text_data)
           message = text_data_json['message']

           # 发送消息到房间组
           await self.channel_layer.group_send(
               self.room_group_name,
               {
                   'type': 'chat_message',
                   'message': message
               }
           )

       # 接收房间组的消息
       async def chat_message(self, event):
           message = event['message']

           # 发送消息到 WebSocket
           await self.send(text_data=json.dumps({
               'message': message
           }))
   ```

### （五）配置 Channel Layer

1. **安装 Redis**

   - Channels 默认使用 Redis 作为消息传递系统，因此需要安装 Redis。

   ```bash
   pip install channels_redis
   ```

2. **修改 `settings.py` 配置 Channel Layer**

   - 在 `settings.py` 中配置 Channel Layer，指定 Redis 作为消息传递中介。可以使用默认内存

   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           # "BACKEND": "channels.layers.InMemoryChannelLayer",  # 开发环境使用内存层
           'CONFIG': {
               "hosts": [('127.0.0.1', 6379)],
           },
       },
   }
   ```

### （六）创建前端界面（window.location.host可以改成后端服务地址）

1. **前端 HTML 文件**

   - 在 `chat` 应用的 `templates` 文件夹下创建一个 `chat_room.html` 文件，用于显示聊天界面并连接 WebSocket。

   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Chat Room</title>
   </head>
   <body>
       <h2>Chat Room: {{ room_name }}</h2>

       <div id="chat-log"></div>
       <input id="chat-message-input" type="text" size="100">
       <button id="chat-message-input-btn">Send</button>

       <script>
           const roomName = "{{ room_name }}";
           const chatSocket = new WebSocket(
               'ws://' + window.location.host + '/ws/chat/' + roomName + '/'
           );

           chatSocket.onmessage = function(e) {
               const data = JSON.parse(e.data);
               document.querySelector('#chat-log').innerHTML += '<br>' + data.message;
           };

           chatSocket.onclose = function(e) {
               console.error('Chat socket closed unexpectedly');
           };

           document.querySelector('#chat-message-input-btn').onclick = function(e) {
               const messageInputDom = document.querySelector('#chat-message-input');
               const message = messageInputDom.value;
               chatSocket.send(JSON.stringify({
                   'message': message
               }));
               messageInputDom.value = '';
           };
       </script>
   </body>
   </html>
   ```

2. **在视图中渲染 HTML**

   - 在 `views.py` 中添加视图，以渲染聊天页面。

   ```python
   from django.shortcuts import render

   def room(request, room_name):
       return render(request, 'chat/chat_room.html', {
           'room_name': room_name
       })
   ```

3. **配置 URL 路由**

   - 在 `urls.py` 中添加 URL 配置。

   ```python
   from django.urls import path
   from . import views

   urlpatterns = [
       path('chat/<str:room_name>/', views.room, name='room'),
   ]
   ```

### （七）运行应用

1. **启动 Redis 服务**

   - 启动 Redis 服务器（确保已安装 Redis）。

   ```bash
   redis-server
   ```

2. **运行 Django 服务器**

   - 最后，使用 Daphne 启动 Django 服务。

   ```bash
   python manage.py runserver
   ```

### （八）测试

1. **访问应用**

   - 在浏览器中访问 `http://127.0.0.1:8000/chat/room_name/`，`room_name` 是聊天房间的名称，多个用户可以同时访问相同的聊天房间，并通过 WebSocket 进行通信。

## 二、总结

通过以上步骤，您已经从零开始搭建了一个支持 WebSocket 的 Django 应用。关键点是安装和配置 `Channels`、使用 `ASGI` 替代 `WSGI` 来支持异步操作，并通过 Redis 实现多客户端的实时消息推送。