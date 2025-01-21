# report/urls.py

from django.urls import path
from .views import ReportGenerationView

urlpatterns = [
    path('generate-report/<str:report_type>/', ReportGenerationView.as_view(), name='generate-report'),
]
