要创建一个用于报表生成的 Django DRF 应用，支持 Excel 和 PDF 格式的报表生成与导出功能，可以分为几个步骤来完成：


1. **集成生成 Excel 和 PDF 的库**：
   - Excel：使用 `openpyxl` 或 `xlsxwriter`。
   - PDF：使用 `reportlab` 或 `weasyprint`。

2. **创建 API 端点**：通过 DRF 提供 Excel 和 PDF 报表的下载接口。

### 一、安装必要的库

首先，安装所需的库：

```bash
pip install openpyxl reportlab 
```

### 二、创建 Django App

假设我们创建一个名为 `report` 的应用，用于报表生成功能。

```bash
python manage.py startapp report_app
```

在 `report` 应用中创建报表生成逻辑。

### 三、实现报表生成功能

#### 1. Excel 报表生成

使用 `openpyxl` 来生成 Excel 格式的报表。

```python
# report/utils.py

from openpyxl import Workbook
from io import BytesIO

def generate_excel_report(data):
    wb = Workbook()
    ws = wb.active

    # 设置表头
    ws.append(["ID", "Name", "Amount"])

    # 填充数据
    for row in data:
        ws.append([row['id'], row['name'], row['amount']])

    # 保存为字节流
    byte_io = BytesIO()
    wb.save(byte_io)
    byte_io.seek(0)
    return byte_io
```

#### 2. PDF 报表生成

使用 `reportlab` 来生成 PDF 格式的报表。

```python
# report/utils.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_pdf_report(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)
    y_position = 750

    # 写入表头
    c.drawString(100, y_position, "ID")
    c.drawString(200, y_position, "Name")
    c.drawString(300, y_position, "Amount")
    y_position -= 20

    # 写入数据
    for row in data:
        c.drawString(100, y_position, str(row['id']))
        c.drawString(200, y_position, row['name'])
        c.drawString(300, y_position, str(row['amount']))
        y_position -= 20

    # 保存为字节流
    c.save()
    buffer.seek(0)
    return buffer
```

#### 3. 创建 API 端点

在 `report/views.py` 中创建 API 端点来返回报表。

```python
# report/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .utils import generate_excel_report, generate_pdf_report

class ReportGenerationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_type):
        # 模拟数据，实际应用中可以从数据库中获取
        data = [
            {"id": 1, "name": "John", "amount": 100},
            {"id": 2, "name": "Jane", "amount": 200},
            {"id": 3, "name": "Doe", "amount": 300}
        ]
        
        if report_type == 'excel':
            file = generate_excel_report(data)
            response = HttpResponse(file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
            return response
        
        elif report_type == 'pdf':
            file = generate_pdf_report(data)
            response = HttpResponse(file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="report.pdf"'
            return response
        
        return Response({"error": "Invalid report type"}, status=status.HTTP_400_BAD_REQUEST)
```

#### 4. 配置 URL 路由

在 `report/urls.py` 配置路由，将报表生成功能暴露为 API 端点。

```python
# report/urls.py

from django.urls import path
from .views import ReportGenerationView

urlpatterns = [
    path('generate-report/<str:report_type>/', ReportGenerationView.as_view(), name='generate-report'),
]
```

#### 5. 注册 URL 路由

确保在主项目的 `urls.py` 中注册 `report` 应用的 URL。

```python
# project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('report/', include('report.urls')),
]
```

### 四、完成后端逻辑

现在，我们已经完成了以下功能：
- 报表生成的 API (`/report/generate-report/excel/` 或 `/report/generate-report/pdf/`)。
- 支持 Excel 和 PDF 格式的报表生成与导出。

### 五、测试

启动 Django 项目并使用 API 请求：
- `GET /report/generate-report/excel/`：下载 Excel 报表。
- `GET /report/generate-report/pdf/`：下载 PDF 报表。

### 六、扩展功能（可选）

1. **分页支持**：当数据量很大时，可以支持分页生成报表。
2. **格式定制**：根据需求，可以自定义报表的格式，如添加更多的表头、内容格式化等。
3. **权限控制**：根据用户权限，限制哪些用户可以下载报表。

这样就完成了一个基本的报表生成 Django DRF 应用，可以根据需要进一步扩展和优化。