# report/utils.py
# report/utils.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
