from django.urls import path
from .views import SSEAPIView

urlpatterns = [
    path('test_sse/', SSEAPIView.as_view(), name='sse'),  # 定义 SSE 接口
]
