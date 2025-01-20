import json
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
  def connect(self):
      # 接受 WebSocket 连接
      self.accept()

  def disconnect(self, close_code):
      # WebSocket 断开连接
      pass

  def receive(self, text_data):
      # 处理接收到的消息
      text_data_json = json.loads(text_data)
      message = text_data_json['message']

      # 发送消息到 WebSocket
      self.send(text_data=json.dumps({
          'message': message
      }))