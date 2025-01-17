from django.urls import path
from .views import SendEmailAPIView, SendEmailWithAttachmentAPIView, SendEmailCodeView, EmailLoginView, \
    PasswordChangeView

urlpatterns = [
    path('send-email', SendEmailAPIView.as_view(), name='send_email'),
    path('send-email-attach', SendEmailWithAttachmentAPIView.as_view(), name='send_email_attach'),
#     邮件验证码
    path('send-email-code/', SendEmailCodeView.as_view(), name='send_email_code'),
    path('email-login/', EmailLoginView.as_view(), name='email_login'),
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),
]
