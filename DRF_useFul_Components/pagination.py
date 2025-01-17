from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'  # 允许通过查询参数设置页面大小
    page_query_param = 'startPages'  # 允许通过查询参数设置当前页
    max_page_size = 100  # 可选，设置最大页面大小
