"""
URL configuration for bibliometria_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from scraper_app.views import dashboard, panel

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # API REST endpoints
    path('panel/', panel, name='panel'),  # Panel de requerimientos
    path('', dashboard, name='dashboard'),  # Dashboard principal
    
    # Servir archivos generados (imágenes, PDFs)
    path('files/<path:path>', serve, {'document_root': settings.BASE_DIR}),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

