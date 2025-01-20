from django.urls import path
from . import views

urlpatterns = [
    path('test_sse/', views.test_sse, name='test_sse'),
]
