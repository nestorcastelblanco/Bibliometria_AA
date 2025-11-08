"""
API URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PapersViewSet,
    SimilarityViewSet,
    FrequenciesViewSet,
    ClustersViewSet,
    visualizations_view,
    trigger_scraper_view,
    trigger_analysis_view,
    scraper_status_view
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'papers', PapersViewSet, basename='papers')
router.register(r'similarity', SimilarityViewSet, basename='similarity')
router.register(r'frequencies', FrequenciesViewSet, basename='frequencies')
router.register(r'clusters', ClustersViewSet, basename='clusters')

urlpatterns = [
    # ViewSets con router
    path('', include(router.urls)),
    
    # Endpoints adicionales
    path('visualizations/<str:filename>/', visualizations_view, name='visualizations'),
    path('trigger-scrape/', trigger_scraper_view, name='trigger-scrape'),
    path('trigger-analysis/', trigger_analysis_view, name='trigger-analysis'),
    path('scraper-status/', scraper_status_view, name='scraper-status'),
]
