"""
Django settings for DRF_useFul_Components project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path
#安装pip install python-decouple
from decouple import Config, RepositoryEnv

# ==========================
# Environment Configuration / 环境配置
# ==========================
# Load environment-specific .env file / 加载特定环境的 .env 文件
ENV = os.getenv('DJANGO_ENV', 'dev')
env_file = f'.env.{ENV}'
config = Config(RepositoryEnv(env_file))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0#=luofq1d%xdz30ly6c=_+lomx@_m&d59d3s@ofm=oky1pmxt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # DRF 框架
    'rest_framework_simplejwt', #simplejwt
    'email_app',
    'upload_files_app'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DRF_useFul_Components.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'DRF_useFul_Components.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================
# Celery Configuration / Celery 配置
# ==========================
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Celery 使用的消息中间件
CELERY_ACCEPT_CONTENT = ['json']  # 接受的消息格式
CELERY_TASK_SERIALIZER = 'json'  # 任务序列化格式


# ==========================
# Email Configuration / 邮件配置
# ==========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 使用 SMTP 作为邮件后端
EMAIL_HOST = 'smtp.163.com'  # 网易邮箱的 SMTP 服务器
EMAIL_PORT = 465  # 网易邮箱的 SSL 端口
EMAIL_USE_TLS = False  # 不使用 TLS
EMAIL_USE_SSL = True  # 使用 SSL 加密
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # 网易邮箱地址
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # 网易邮箱授权码
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Your Project <no-reply@example.com>')  # 默认发件人



# ==========================
# REST Framework Configuration / REST 框架配置
# ==========================
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'DRF_useFul_Components.pagination.CustomPagination',  # 自定义分页类
    'PAGE_SIZE': 10,  # 默认分页大小
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT 认证
    # ],
    # 'DEFAULT_PERMISSION_CLASSES': [],  # 默认权限类
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=15),  # 访问令牌过期时间
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # 刷新令牌过期时间
    'ROTATE_REFRESH_TOKENS': True,  # 是否旋转刷新令牌
    'BLACKLIST_AFTER_ROTATION': True,  # 刷新后将旧令牌列入黑名单
    'ALGORITHM': 'HS256',  # 加密算法
    'SIGNING_KEY': config('JWT_SIGNING_KEY', default='your-secret-key'),  # 签名密钥
    'VERIFYING_KEY': None,  # 验证密钥
}
