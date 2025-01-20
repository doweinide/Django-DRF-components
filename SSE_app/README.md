## 跨域
 pip install django-cors-headers


ALLOWED_HOSTS = ['192.168.1.9','127.0.0.1','http://localhost:5778']

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5778',  # 允许的域名
    'http://127.0.0.1',
    'http://192.168.1.9',     # 另一个允许的域名
]

INSTALLED_APPS = [

    'corsheaders',#跨域问题

]

MIDDLEWARE = [

    'corsheaders.middleware.CorsMiddleware',#跨域问题
    'django.middleware.common.CommonMiddleware',
 
]
## 异步
pip install daphne

ASGI_APPLICATION = "DRF_useFul_Components.asgi.application"


INSTALLED_APPS = [

    'daphne',  # 异步（SSE）

]
