from django.http import StreamingHttpResponse
from rest_framework.views import APIView
import time
import logging

# 创建日志记录器
logger = logging.getLogger(__name__)

class SSEAPIView(APIView):
    """基于 DRF 的 SSE 视图"""

    def get(self, request, *args, **kwargs):
        # 生成事件流
        def event_stream():
            try:
                for i in range(1, 11):  # 模拟 10 条数据
                    yield f"data: Event {i} received\n\n"
                    logger.info(f"Sent event {i}")  # 添加日志记录
                    time.sleep(1)  # 模拟延时
            except GeneratorExit:
                # 捕获客户端断开连接的情况
                logger.warning("Client disconnected during streaming")
            except Exception as e:
                # 捕获其他异常并记录日志
                logger.error(f"Error during streaming: {e}")
                yield f"data: Error occurred: {str(e)}\n\n"

        # 创建 StreamingHttpResponse
        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'

        # Django 通常会自动处理 `Transfer-Encoding: chunked`，手动设置可能导致问题
        # 如果确实需要明确设置，请确认你的反向代理服务器支持该特性
        response['Transfer-Encoding'] = 'chunked'

        return response
