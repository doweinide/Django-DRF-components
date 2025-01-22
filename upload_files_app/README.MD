### Django 应用文档：普通文件上传与断点分片上传大文件

#### 1. **概述**
本 Django 应用提供了两种文件上传功能：
- 普通文件上传
- 断点分片上传大文件

该应用能够处理文件的上传、分块存储、文件哈希检查、上传进度管理等任务。通过这些功能，用户可以上传较大的文件，而无需担心上传中断。

#### 2. **项目准备**
要将该 Django 应用移植到新的环境或项目中，您需要按照以下步骤进行配置：

##### 2.1 **创建 Django 项目（如果没有）**
如果您还没有创建 Django 项目，请使用以下命令创建项目：
```bash
django-admin startproject your_project
cd your_project
```

##### 2.2 **创建应用**
如果该功能是作为一个新的 Django 应用添加的，请创建一个新的应用：
```bash
python manage.py startapp file_upload
```

#### 3. **迁移与数据库配置**

##### 3.1 **创建模型**
该应用使用 `File` 模型来存储上传的文件。模型定义了以下字段：
- `file_name`: 文件的原始名称（字符串）
- `file_path`: 文件存储路径（使用 `FileField` 处理）
- `file_hash`: 文件的哈希值，用于唯一标识文件

**models.py 示例：**
```python
from django.db import models

class File(models.Model):
    file_name = models.CharField(max_length=255)  # 文件原始名称
    file_path = models.FileField(upload_to='uploads/files/')  # 文件存储路径
    file_hash = models.CharField(max_length=64, unique=True)  # 文件的哈希值，唯一约束
```

##### 3.2 **生成迁移文件**
在 Django 中进行模型更改后，您需要生成并应用迁移文件：
```bash
python manage.py makemigrations
```

##### 3.3 **应用迁移**
运行以下命令以在数据库中创建所需的表：
```bash
python manage.py migrate
```

#### 4. **文件上传设置**

在 `settings.py` 中配置文件上传的设置：
- `MEDIA_URL`: 定义访问文件的 URL 路径。
- `MEDIA_ROOT`: 定义文件存储的本地路径。

示例配置：
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

确保 `urls.py` 配置了对媒体文件的正确访问：
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 其他 URL 路由
]

# 确保本地开发环境下能够访问到媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### 5. **API 视图**

应用包含以下 API 视图：
- **`UploadFileView`**：用于上传普通文件。
- **`UploadChunkView`**：用于上传文件分块。
- **`GetUploadedChunksView`**：查询已上传的文件分块索引。
- **`CompleteUploadView`**：合并分块文件为完整文件。

##### 5.1 **普通文件上传视图** (`UploadFileView`)
普通文件上传功能用于处理标准文件上传。该视图处理用户上传的普通文件，并将文件保存到指定的目录中。根据文件的类型，应用会对上传的文件进行类型判断，并限制文件大小。

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage
from .utils import get_file_type, MAX_UPLOAD_SIZES
from .models import File

class UploadFileView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_type = get_file_type(file)
        file_size_limit = MAX_UPLOAD_SIZES.get(file_type, 10 * 1024 * 1024)  # Default to 10MB

        if file.size > file_size_limit:
            return Response({'error': f'File size exceeds {file_size_limit // (1024 * 1024)}MB'}, status=status.HTTP_400_BAD_REQUEST)

        # 保存文件
        file_storage = FileSystemStorage()
        file_path = file_storage.save(file.name, file)
        file_url = file_storage.url(file_path)

        # 保存文件信息到数据库
        file_instance = File.objects.create(file_name=file.name, file_path=file_url, file_hash=file_hash(file))
        
        return Response({'message': 'File uploaded successfully', 'filePath': file_url}, status=status.HTTP_201_CREATED)
```

##### 5.2 **获取已上传的分块视图** (`GetUploadedChunksView`)
用于查询当前文件的已上传分块。这对于断点续传的功能至关重要。

```python
class GetUploadedChunksView(APIView):
    def get(self, request):
        """
        查询已上传的分块索引
        """
        file_hash = request.query_params.get('fileHash')
        if not file_hash:
            return Response({'error': 'Missing fileHash parameter'}, status=400)

        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_hash)
        if not os.path.exists(temp_dir):
            return Response({'uploadedChunks': []})

        # 获取所有已上传的分块索引
        uploaded_chunks = [
            int(filename.split('_')[1])
            for filename in os.listdir(temp_dir)
            if filename.startswith('chunk_')
        ]
        uploaded_chunks.sort()
        return Response({'uploadedChunks': uploaded_chunks})
```

##### 5.3 **文件分块上传视图** (`UploadChunkView`)
用于上传文件的分块并存储。该视图会接收分块并暂存它们，然后返回一个响应告知客户端是否上传成功。

```python
class UploadChunkView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        chunk_index = request.data.get('chunkIndex')
        file_hash = request.data.get('fileHash')
        total_chunks = request.data.get('totalChunks')

        # 校验参数
        if not all([file, chunk_index, file_hash, total_chunks]):
            return Response({'error': 'Missing required parameters'}, status=400)

        # 存储文件分块
        file_type = get_file_type(file)
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_hash)
        os.makedirs(temp_dir, exist_ok=True)

        chunk_path = os.path.join(temp_dir, f'chunk_{chunk_index}')
        with open(chunk_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        return Response({'message': 'Chunk uploaded successfully'})
```

##### 5.4 **合并上传的分块视图** (`CompleteUploadView`)
用于合并所有上传的文件分块，生成完整的文件。

```python
class CompleteUploadView(APIView):
    def post(self, request):
        file_hash = request.data.get('fileHash')
        file_extension = request.data.get('fileExtension')
        
        if not file_hash or not file_extension:
            return Response({'error': 'Missing required parameters'}, status=400)

        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_hash)
        if not os.path.exists(temp_dir):
            return Response({'error': 'No uploaded chunks found'}, status=400)

        output_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', get_file_type(file_extension))
        os.makedirs(output_dir, exist_ok=True)

        output_file_path = os.path.join(output_dir, f'{file_hash}.{file_extension}')
        chunk_files = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir)], key=lambda x: int(os.path.basename(x).split('_')[1]))

        with open(output_file_path, 'wb') as output_file:
            for chunk_file in chunk_files:
                with open(chunk_file, 'rb') as f:
                    output_file.write(f.read())

        # 删除临时分块文件
        for chunk_file in chunk_files:
            os.remove(chunk_file)
        os.rmdir(temp_dir)

        return Response({'message': 'Upload complete', 'filePath': output_file_path})
```

#### 6. **上传文件类型与大小配置**

在应用中，文件类型及其对应的最大上传大小被配置在 `settings.py` 中：

```python
MAX_UPLOAD_SIZES = {
    'images': 5 * 1024 * 1024,  # 最大图片上传大小：5MB
    'videos': 50 * 1024 * 1024,  # 最大视频上传大小：50MB
    'audio': 20 * 1024 * 1024,   # 最大音频上传大小：20MB
    'documents': 10 * 1024 * 1024,  # 最大文档上传大小：10MB
    'archives': 50 * 1024 * 1024,  # 最大压缩文件上传大小：50MB
    'others': 10 * 1024 * 1024,  # 其他文件类型上传大小：10MB
}
```

#### 7. **前端配置**

前端需要支持文件选择、分块上传、上传进度管理、暂停/继续上传等功能。您可以使用 `Vue.js` 与 `axios` 进行前端实现。

#### 8. **迁移步骤**
如果您需要将此应用迁移到其他项目中，按以下步骤操作：

1. **复制应用代码**：将 `file_upload` 应用复制到新的项目中（包括 `views.py`、`models.py`、`serializers.py` 等文件）。
2. **更新项目的 `INSTALLED_APPS`**：在新项目的 `settings.py` 中，添加 `file_upload` 应用。
   ```python
   INSTALLED_APPS = [
       # 其他应用
       'file_upload',
   ]
   ```
3. **迁移数据库**：运行 `makemigrations` 和 `migrate`，以确保数据库表被正确创建。
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **配置静态文件和媒体文件**：确保 `MEDIA_URL` 和 `MEDIA_ROOT` 配置正确，并且在开发环境中可以访问媒体文件。

#### 9. **总结**
通过以上步骤，您可以将该 Django 应用成功移植到新的项目中，并且能够支持普通文件上传和断点分片上传大文件。确保数据库迁移、静态文件和媒体文件配置正确，您就可以顺利进行文件上传处理。