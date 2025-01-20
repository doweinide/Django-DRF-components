# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 从 URL 获取 room_name 参数
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        print('加入的房间组',self.room_name)
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 接受连接
        await self.accept()

    async def disconnect(self, close_code):
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # 处理从 WebSocket 收到的数据
        print('获取的数据',text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 将消息发送到房间组
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # 从房间组收到消息后，将消息发送给 WebSocket
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
