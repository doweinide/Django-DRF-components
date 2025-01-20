# sse_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.stock_price_view, name='sse_view'),
]
