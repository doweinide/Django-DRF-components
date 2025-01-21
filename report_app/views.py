# report/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from .utils import generate_excel_report, generate_pdf_report
from math import ceil


class ReportGenerationView(APIView):
    # permission_classes = [IsAuthenticated]  # 可选，保留或启用身份验证

    def get(self, request, report_type):
        # 获取分页参数
        page = int(request.GET.get('page', 1))  # 默认为第一页
        page_size = int(request.GET.get('page_size', 10))  # 每页条数，默认为 10
        file_name = request.GET.get('file_name', 'report')  # 默认为 'report'

        # 模拟数据，实际应用中可以从数据库中获取
        data = [
            {"id": 1, "name": "John", "amount": 100},
            {"id": 2, "name": "Jane", "amount": 200},
            {"id": 3, "name": "Doe", "amount": 300},
            {"id": 4, "name": "Alice", "amount": 400},
            {"id": 5, "name": "Bob", "amount": 500},
            {"id": 6, "name": "Charlie", "amount": 600},
            {"id": 7, "name": "David", "amount": 700},
            {"id": 8, "name": "Eva", "amount": 800},
            {"id": 9, "name": "Frank", "amount": 900},
            {"id": 10, "name": "Grace", "amount": 1000},
            {"id": 11, "name": "Hank", "amount": 1100},
            {"id": 12, "name": "Ivy", "amount": 1200},
            {"id": 13, "name": "Jack", "amount": 1300},
            {"id": 14, "name": "Lily", "amount": 1400},
            {"id": 15, "name": "Mason", "amount": 1500}
        ]

        # 计算分页
        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = data[start:end]

        # 计算总页数
        total_pages = ceil(len(data) / page_size)

        # 根据 report_type 生成报表
        if report_type == 'excel':
            file = generate_excel_report(paginated_data)
            response = HttpResponse(file,
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{file_name}.xlsx"'
            response['X-Total-Pages'] = total_pages  # 可选，返回总页数
            return response

        elif report_type == 'pdf':
            file = generate_pdf_report(paginated_data)
            response = HttpResponse(file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{file_name}.pdf"'
            response['X-Total-Pages'] = total_pages  # 可选，返回总页数
            return response

        return Response({"error": "Invalid report type"}, status=status.HTTP_400_BAD_REQUEST)
