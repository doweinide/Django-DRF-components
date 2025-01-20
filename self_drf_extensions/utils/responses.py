from rest_framework.response import Response

def custom_response(data, status_code=200, message="success"):
    """
    自定义的 Response 格式。
    """
    return Response({
        "status_code": status_code,
        "message": message,
        "data": data
    })
