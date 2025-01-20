from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def test_sse(request):
    return render(request, 'testSSE.html')
