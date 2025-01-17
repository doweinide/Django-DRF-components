# myapp/tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html
from django.conf import settings

@shared_task
def send_email_code(email, code):
    # 生成 HTML 邮件内容
    html_content = format_html(
        """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px; padding: 20px; background-color: #f9f9f9;">
            <h2 style="text-align: center; color: #007bff;">您的登录验证码</h2>
            <p>您好，</p>
            <p>我们收到了您的登录请求。以下是您的验证码：</p>
            <div style="text-align: center; margin: 20px 0;">
                <span style="font-size: 24px; font-weight: bold; color: #333;">{}</span>
            </div>
            <p style="color: #555;">该验证码有效期为 <strong>5分钟</strong>。请勿将验证码泄露给他人。</p>
            <hr style="border: none; border-top: 1px solid #ddd;">
            <p style="text-align: center; font-size: 12px; color: #888;">如果您未请求此验证码，请忽略此邮件。</p>
        </div>
        """, code
    )

    # 发送邮件
    try:
        subject = "您的登录验证码"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        message = EmailMultiAlternatives(subject, body="", from_email=from_email, to=to_email)
        message.attach_alternative(html_content, "text/html")
        message.send()
    except Exception as e:
        return f"邮件发送失败: {str(e)}"
    return "邮件已成功发送"
