
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.core.cache import cache
from datetime import datetime
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from email_app.tasks import send_email_code

# 获取用户模型，使用 Django 自带的 User 模型
User = get_user_model()

# *************************************** 用户邮箱登录，设置密码，邮箱验证码 ***************************************

class SendEmailCodeView(APIView):
    """
    生成并向用户邮箱发送登录验证码
    请求示例：
    {
        "email": "example@example.com"
    }
    """
    def post(self, request):
        # 获取邮箱地址
        email = request.data.get('email')
        if not email:
            return Response({"error": "邮箱是必填项"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查用户是否存在
        users = User.objects.filter(email=email)
        if not users.exists():
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        # user = users.first()

        # 生成六位随机验证码
        code = f"{random.randint(100000, 999999)}"

        # 将验证码存入缓存（有效期5分钟）
        cache.set(email, {"code": code, "created_at": datetime.now().isoformat()}, timeout=300)

        # 调用 Celery 异步任务发送验证码邮件
        send_email_code.delay(email, code)

        # 返回成功信息
        return Response({"message": "验证码已成功发送"}, status=status.HTTP_200_OK)


class EmailLoginView(APIView):
    """
    使用邮箱和验证码登录
    请求示例：
    {
        "email": "example@example.com",
        "code": "123456"
    }
    """
    def post(self, request):
        # 获取请求中的邮箱和验证码
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "邮箱和验证码是必填项"}, status=status.HTTP_400_BAD_REQUEST)

        # 从缓存中获取验证码信息
        cache_value = cache.get(email)
        if not cache_value:
            return Response({"error": "验证码已过期或未发送"}, status=status.HTTP_400_BAD_REQUEST)

        stored_code = cache_value.get("code")
        created_at = cache_value.get("created_at")

        # 验证验证码是否过期（有效期5分钟）
        created_time = datetime.fromisoformat(created_at)
        if (datetime.now() - created_time).total_seconds() > 300:
            return Response({"error": "验证码已过期"}, status=status.HTTP_400_BAD_REQUEST)

        # 验证用户输入的验证码是否正确
        if stored_code != code:
            return Response({"error": "验证码错误"}, status=status.HTTP_400_BAD_REQUEST)

        # 查找用户
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 返回登录成功信息
        response_data = {
            "user": {
                "email": user.email,
                "username": user.username,
            },
            "message": "登录成功"
        }
        return Response(response_data, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    """
    使用验证码修改用户密码
    请求示例：
    {
        "email": "example@example.com",
        "code": "123456",
        "new_password": "newPassword123"
    }
    """
    def post(self, request):
        # 获取请求中的邮箱、验证码和新密码
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        if not email or not code or not new_password:
            return Response({"error": "邮箱、验证码和新密码是必填项"}, status=status.HTTP_400_BAD_REQUEST)

        # 从缓存中获取验证码信息
        cache_value = cache.get(email)
        if not cache_value:
            return Response({"error": "验证码已过期或未发送"}, status=status.HTTP_400_BAD_REQUEST)

        stored_code = cache_value.get("code")
        created_at = cache_value.get("created_at")

        # 验证验证码是否过期（有效期5分钟）
        created_time = datetime.fromisoformat(created_at)
        if (datetime.now() - created_time).total_seconds() > 300:
            return Response({"error": "验证码已过期"}, status=status.HTTP_400_BAD_REQUEST)

        # 验证验证码是否正确
        if stored_code != code:
            return Response({"error": "验证码错误"}, status=status.HTTP_400_BAD_REQUEST)

        # 查找用户并更新密码
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        return Response({"message": "密码修改成功"}, status=status.HTTP_200_OK)


# ************************************************ 测试邮件发送 ************************************************

class SendEmailAPIView(APIView):
    """
    发送普通邮件
    请求示例：
    {
        "subject": "测试邮件",
        "message": "这是一个测试邮件。",
        "recipients": ["recipient1@example.com"]
    }
    """
    def post(self, request, *args, **kwargs):
        # 获取邮件主题、内容和接收者列表
        subject = request.data.get('subject', '默认主题')
        message = request.data.get('message', '默认消息内容')
        recipient_list = request.data.get('recipients', ['recipient@example.com'])

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
            return Response({"message": "邮件发送成功！"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class SendEmailWithAttachmentAPIView(APIView):
    """
    发送带附件的邮件
    请求示例：
    {
        "subject": "测试邮件",
        "message": "这是一个带附件的测试邮件。",
        "recipients": ["recipient1@example.com"],
        "attachment": 文件对象
    }
    """
    def post(self, request, *args, **kwargs):
        # 获取邮件主题、内容和接收者列表
        subject = request.data.get('subject', '默认主题')
        message = request.data.get('message', '默认消息内容')
        recipient_list = request.data.get('recipients', ['recipient@example.com'])
        attachment = request.FILES.get('attachment')  # 获取附件

        try:
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
            )

            # 如果有附件则添加
            if attachment:
                email.attach(attachment.name, attachment.read(), attachment.content_type)

            email.send(fail_silently=False)
            return Response({"message": "邮件发送成功！"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
