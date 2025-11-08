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
from .views_results import (
    get_similarity_details,
    calculate_similarity,
    get_frequencies_details,
    get_clustering_results,
    get_sorting_results,
    get_graph_info
)
from .views_execute import (
    run_req2,
    run_req3,
    run_req4,
    run_req5,
    run_grafos_cit,
    run_grafos_terms,
    list_assets
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
    
    # Endpoints de resultados detallados
    path('similarity/details/', get_similarity_details, name='similarity-details'),
    path('similarity/calculate/', calculate_similarity, name='similarity-calculate'),
    path('frequencies/details/', get_frequencies_details, name='frequencies-details'),
    path('clustering/results/', get_clustering_results, name='clustering-results'),
    path('sorting/results/', get_sorting_results, name='sorting-results'),
    path('graphs/info/', get_graph_info, name='graph-info'),
    
    # Endpoints para ejecutar requerimientos (Panel)
    path('req2', run_req2, name='run-req2'),
    path('req3', run_req3, name='run-req3'),
    path('req4', run_req4, name='run-req4'),
    path('req5', run_req5, name='run-req5'),
    path('grafos/cit', run_grafos_cit, name='run-grafos-cit'),
    path('grafos/terms', run_grafos_terms, name='run-grafos-terms'),
    path('list_assets', list_assets, name='list-assets'),
]
