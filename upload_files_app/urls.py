from django.urls import path
from .views import (
    UploadChunkView,
    GetUploadedChunksView,
    CompleteUploadView,
    UploadFileView,
)

urlpatterns = [
    # ==========================
    # 分片上传
    # ==========================
    path('upload/videos', UploadChunkView.as_view(), name='upload_chunk'),
    path('upload/uploaded-chunks', GetUploadedChunksView.as_view(), name='get_uploaded_chunks'),
    path('upload/complete', CompleteUploadView.as_view(), name='complete_upload'),

    # ==========================
    # 普通上传
    # ==========================
    path('upload/file', UploadFileView.as_view(), name='upload_file'),
]
