from django.shortcuts import render

# Create your views here.
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.conf import settings

# ==========================
# 普通文件上传
# ==========================
class UploadFileView(APIView):
    """
    视图作用：
    - 处理普通文件上传，将完整文件直接保存到目标目录。

    主要逻辑：
    1. 接收上传的文件 (file)。
    2. 检查文件是否存在。
    3. 将文件保存到指定的存储路径。
    4. 返回上传成功的消息和文件路径。
    """
    parser_classes = [MultiPartParser]  # 支持文件上传解析

    def post(self, request):
        # 从请求中获取文件
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file uploaded'}, status=400)

        # 确定文件保存路径
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/files')
        os.makedirs(output_dir, exist_ok=True)  # 确保目录存在
        output_file_path = os.path.join(output_dir, uploaded_file.name)

        # 保存文件到目标路径
        with open(output_file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # 返回成功响应
        return Response({
            'message': 'File uploaded successfully',
            'filePath': output_file_path  # 返回文件存储路径
        })


# ==========================
# 断点上传，分片上传
# ==========================

class UploadChunkView(APIView):
    # 指定解析器，支持文件上传
    parser_classes = [MultiPartParser]

    def post(self, request):
        """
        视图作用：
        - 接收文件分块并保存到服务器的临时目录。

        主要逻辑：
        1. 获取客户端传递的文件分块 (file)、分块索引 (chunkIndex)、文件哈希值 (fileHash) 和总分块数 (totalChunks)。
        2. 检查是否缺少必需的参数，如果缺少则返回 400 错误。
        3. 检查完整文件是否已存在。如果存在，返回 'uploadedChunks: completed'。
        4. 如果文件未完成上传，将分块文件保存到临时目录。
        5. 返回确认消息 'Chunk uploaded successfully'。
        """
        file = request.FILES.get('file')
        chunk_index = request.data.get('chunkIndex')
        file_hash = request.data.get('fileHash')
        total_chunks = request.data.get('totalChunks')

        # 参数校验
        if not all([file, chunk_index, file_hash, total_chunks]):
            return Response({'error': 'Missing required parameters'}, status=400)

        # 检查完整文件是否已存在
        final_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads/videos', f'{file_hash}.mp4')  # 假设文件存储为 .mp4
        if os.path.exists(final_file_path):
            return Response({'uploadedChunks': 'completed'})  # 文件已上传完成

        # 保存分块到临时目录
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_hash)
        os.makedirs(temp_dir, exist_ok=True)
        chunk_path = os.path.join(temp_dir, f'chunk_{chunk_index}')

        # 写入分块文件
        with open(chunk_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # 返回上传成功消息
        return Response({'message': 'Chunk uploaded successfully'})


class GetUploadedChunksView(APIView):
    def get(self, request):
        """
        视图作用：
        - 查询已上传的文件分块索引列表。

        主要逻辑：
        1. 接收文件哈希值参数 (fileHash)。
        2. 检查对应的临时目录是否存在：
           - 如果不存在，返回空列表。
           - 如果存在，获取该目录下所有的分块文件。
        3. 提取分块索引并排序，返回给客户端。
        """
        file_hash = request.query_params.get('fileHash')
        if not file_hash:
            return Response({'error': 'Missing fileHash parameter'}, status=400)

        # 临时目录路径
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_hash)
        if not os.path.exists(temp_dir):
            return Response({'uploadedChunks': []})  # 没有分块上传记录

        # 获取所有已上传的分块索引
        uploaded_chunks = [
            int(filename.split('_')[1])
            for filename in os.listdir(temp_dir)
            if filename.startswith('chunk_')
        ]
        uploaded_chunks.sort()  # 对分块索引进行排序

        # 返回已上传的分块索引
        return Response({'uploadedChunks': uploaded_chunks})


class CompleteUploadView(APIView):
    def post(self, request):
        """
        视图作用：
        - 合并分块文件生成完整文件，并清理临时目录。

        主要逻辑：
        1. 接收文件哈希值参数 (fileHash)。
        2. 检查对应的临时目录是否存在：
           - 如果不存在，返回错误响应。
        3. 确保目标目录存在。
        4. 按分块文件的索引顺序合并所有分块为完整文件。
        5. 合并完成后，删除分块文件并清理临时目录。
        6. 返回上传完成消息，并提供完整文件路径。
        """
        file_hash = request.data.get('fileHash')
        if not file_hash:
            return Response({'error': 'Missing fileHash parameter'}, status=400)

        # 临时目录路径
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_hash)
        if not os.path.exists(temp_dir):
            return Response({'error': 'No uploaded chunks found'}, status=400)

        # 确保输出目录存在
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/videos')
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads/videos', f'{file_hash}.mp4')

        # 按分块顺序合并文件
        chunk_files = sorted(
            [os.path.join(temp_dir, f) for f in os.listdir(temp_dir)],
            key=lambda x: int(os.path.basename(x).split('_')[1])  # 按分块索引排序
        )

        # 合并分块到最终文件
        with open(output_file_path, 'wb') as output_file:
            for chunk_file in chunk_files:
                with open(chunk_file, 'rb') as f:
                    output_file.write(f.read())

        # 清理临时目录
        for chunk_file in chunk_files:
            os.remove(chunk_file)
        os.rmdir(temp_dir)

        # 返回合并完成消息
        return Response({'message': 'Upload complete', 'filePath': output_file_path})
