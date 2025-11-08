"""
Views para el frontend web
"""
from django.shortcuts import render


def dashboard(request):
    """Dashboard principal con interfaz web"""
    return render(request, 'dashboard.html')

