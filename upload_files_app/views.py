from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import render

# Create your views here.
import os
import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.conf import settings

# ==========================
# 普通文件上传
# ==========================
from .models import File
from .serializers import FileSerializer
class UploadFileView(APIView):
    """
    视图作用：
    - 处理文件上传，按文件内容的哈希值重命名文件，并保存到分类目录。
    - 使用哈希值避免重复文件存储。
    - 根据文件类型限制文件大小。
    window访问类似
    ：http://127.0.0.1:8000/media/C:/back/Django-DRF-components/media/uploads/files/images/171fb803939c5efaa68f1874c91e4ba4ab73936fd01e0cece46d45ecad667982.jpg
    """

    parser_classes = [MultiPartParser]

    def post(self, request):
        # 获取上传的文件
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No file uploaded'}, status=400)

        # 获取文件类型
        file_type = get_file_type(uploaded_file)

        # 检查文件大小
        max_size = settings.MAX_UPLOAD_SIZES.get(file_type, settings.MAX_UPLOAD_SIZES['others'])
        if uploaded_file.size > max_size:
            return Response({
                'error': f'The file is too large. Maximum allowed size for {file_type} is {max_size / 1024 / 1024} MB.'
            }, status=400)

        # 计算文件的哈希值
        file_data = uploaded_file.read()
        file_hash = hashlib.sha256(file_data).hexdigest()

        # 检查文件是否已存在于数据库
        existing_file = File.objects.filter(file_hash=file_hash).first()

        if existing_file:
            # 如果文件已经存在，返回已存在的文件路径
            # 如果文件已经存在，使用序列化器返回文件信息
            serializer = FileSerializer(existing_file)
            return Response({
                'message': 'File already exists',
                'filePath': serializer.data['file_path'],  # 正确访问方式
                'fileHash': serializer.data['file_hash'],
                'fileName': serializer.data['file_name']
            })

        # 确定文件存储路径
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'files', file_type)
        print(output_dir,'output_idr')
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, f"{file_hash}{os.path.splitext(uploaded_file.name)[1]}")

        # 保存文件到目标路径
        with open(output_file_path, 'wb') as f:
            f.write(file_data)

        # 创建文件记录并保存
        file_record = File.create_file_record(uploaded_file, output_file_path)

        # 使用序列化器返回响应
        serializer = FileSerializer(file_record)

        return Response({
            'message': 'File uploaded successfully',
            'filePath': output_file_path,  # 使用 URL 返回
            'fileHash': file_record.file_hash,
            'fileName': file_record.file_name
        })



# ==========================
# 文件类型判断函数
# ==========================
def get_file_type(file) -> str:
    """
    根据文件的扩展名判断文件类型
    :param file: 上传的文件
    :return: 文件类型字符串（如 'images'、'videos' 等）
    """
    file_extension = file.name.split('.')[-1].lower()

    if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
        return 'images'
    elif file_extension in ['mp4', 'avi', 'mov', 'mkv']:
        return 'videos'
    elif file_extension in ['mp3', 'wav', 'flac']:
        return 'audio'
    elif file_extension in ['pdf', 'doc', 'docx', 'xls', 'xlsx']:
        return 'documents'
    elif file_extension in ['zip', 'tar', 'rar']:
        return 'archives'
    else:
        return 'others'


# ==========================
# 断点上传，分片上传视图
# ==========================
class UploadChunkView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        """
        上传文件分块
        """
        file = request.FILES.get('file')
        chunk_index = request.data.get('chunkIndex')
        file_hash = request.data.get('fileHash')
        total_chunks = request.data.get('totalChunks')

        if not all([file, chunk_index, file_hash, total_chunks]):
            return Response({'error': 'Missing required parameters'}, status=400)

        # 动态设置存储路径
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_hash)
        os.makedirs(temp_dir, exist_ok=True)

        # 保存分块到临时目录
        chunk_path = os.path.join(temp_dir, f'chunk_{chunk_index}')
        with open(chunk_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        return Response({'message': 'Chunk uploaded successfully'})


class GetUploadedChunksView(APIView):
    def get(self, request):
        """
        查询已上传的分块索引
        """
        file_hash = request.query_params.get('fileHash')
        if not file_hash:
            return Response({'error': 'Missing fileHash parameter'}, status=400)

        # 检查数据库中是否存在完整文件
        try:
            file_record = File.objects.get(file_hash=file_hash)
            file_serializer = FileSerializer(file_record)
            return Response({
                'uploadedChunks': 'completed',
                'file': file_serializer.data
            })
        except File.DoesNotExist:
            pass

        # 检查临时目录中的分块
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_hash)
        if not os.path.exists(temp_dir):
            return Response({'uploadedChunks': []})

        uploaded_chunks = [
            int(filename.split('_')[1])
            for filename in os.listdir(temp_dir)
            if filename.startswith('chunk_')
        ]
        uploaded_chunks.sort()
        return Response({'uploadedChunks': uploaded_chunks})


class CompleteUploadView(APIView):
    def post(self, request):
        """
        合并分块文件并保存到数据库
        """
        file_hash = request.data.get('fileHash')
        file_extension = request.data.get('fileExtension')  # 从客户端获取文件扩展名
        file_name = request.data.get('fileName')  # 文件原始名称

        if not all([file_hash, file_extension, file_name]):
            return Response({'error': 'Missing required parameters'}, status=400)

        # 确保临时目录存在
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_hash)
        if not os.path.exists(temp_dir):
            return Response({'error': 'No uploaded chunks found'}, status=400)

        # 确保输出目录存在
        file_type = get_file_type(SimpleUploadedFile(f'temp.{file_extension}', b''))
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', file_type)
        os.makedirs(output_dir, exist_ok=True)

        # 动态设置完整文件路径
        output_file_path = os.path.join(output_dir, f'{file_hash}.{file_extension}')

        # 按分块顺序合并文件
        chunk_files = sorted(
            [os.path.join(temp_dir, f) for f in os.listdir(temp_dir)],
            key=lambda x: int(os.path.basename(x).split('_')[1])
        )
        with open(output_file_path, 'wb') as output_file:
            for chunk_file in chunk_files:
                with open(chunk_file, 'rb') as f:
                    output_file.write(f.read())

        # 清理临时目录
        for chunk_file in chunk_files:
            os.remove(chunk_file)
        os.rmdir(temp_dir)

        # 保存文件记录到数据库
        file_record = File.objects.create(
            file_name=file_name,
            file_path=output_file_path.replace(settings.MEDIA_ROOT, '').lstrip('/'),
            file_hash=file_hash
        )
        file_serializer = FileSerializer(file_record)

        return Response({
            'message': 'Upload complete',
            'file': file_serializer.data
        })