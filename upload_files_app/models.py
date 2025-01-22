from django.db import models
import hashlib

class File(models.Model):
    file_name = models.CharField(max_length=255)  # 文件原始名称
    file_path = models.FileField(upload_to='uploads/files/')  # 文件存储路径，使用 FileField 来处理
    file_hash = models.CharField(max_length=64, unique=True)  # 文件的哈希值，唯一约束

    def __str__(self):
        return self.file_name

    @classmethod
    def create_file_record(cls, uploaded_file, file_path):
        """
        根据文件哈希值创建或返回文件记录
        :param uploaded_file: 上传的文件对象
        :param file_path: 文件的存储路径
        :return: 文件记录对象
        """
        # 计算文件的哈希值
        uploaded_file.seek(0)  # 重新将文件指针移动到开头，准备下一步操作
        file_hash = hashlib.sha256(uploaded_file.read()).hexdigest()

        # 查找是否已存在该文件
        file_record, created = cls.objects.get_or_create(
            file_hash=file_hash,
            defaults={'file_name': uploaded_file.name, 'file_path': file_path}
        )

        # 如果文件已存在，返回已存在的记录
        if not created:
            return file_record

        # 如果是新文件，则返回新的记录
        return file_record
