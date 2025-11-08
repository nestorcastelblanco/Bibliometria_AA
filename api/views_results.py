"""
API Views adicionales para resultados detallados
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from pathlib import Path
import pandas as pd
import json


@api_view(['GET'])
def get_similarity_details(request):
    """
    GET /api/similarity/details/
    Devuelve los datos de similitud para mostrar en tabla
    """
    try:
        processed_dir = settings.DATA_PROCESSED
        csv_file = processed_dir / 'reporte_similitud_top.csv'
        
        if not csv_file.exists():
            return Response({
                'error': 'No hay resultados. Ejecuta el análisis primero.',
                'available': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        df = pd.read_csv(csv_file)
        
        return Response({
            'available': True,
            'total_pairs': len(df),
            'columns': list(df.columns),
            'data': df.head(50).to_dict(orient='records')  # Top 50 pares
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def calculate_similarity(request):
    """
    POST /api/similarity/calculate/
    Body: {"doc_ids": [0, 3, 7]}
    Calcula similitud entre documentos específicos
    """
    try:
        doc_ids = request.data.get('doc_ids', [])
        
        if not doc_ids or len(doc_ids) < 2:
            return Response({
                'error': 'Debes proporcionar al menos 2 IDs de documentos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Implementar cálculo de similitud específico
        # Por ahora, devolvemos mensaje
        return Response({
            'message': f'Calculando similitud entre documentos: {doc_ids}',
            'doc_ids': doc_ids,
            'status': 'pending'
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_frequencies_details(request):
    """
    GET /api/frequencies/details/
    Devuelve términos más frecuentes
    """
    try:
        processed_dir = settings.DATA_PROCESSED
        
        # Buscar archivo de términos
        json_file = processed_dir / 'términos_grafos.json'
        
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraer top términos
            if isinstance(data, dict) and 'terms' in data:
                terms = data['terms']
                top_terms = sorted(terms.items(), key=lambda x: x[1], reverse=True)[:30]
                
                return Response({
                    'available': True,
                    'total_terms': len(terms),
                    'top_terms': [{'term': t[0], 'frequency': t[1]} for t in top_terms]
                })
        
        return Response({
            'error': 'No hay resultados de frecuencias',
            'available': False
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_clustering_results(request):
    """
    GET /api/clustering/results/
    Devuelve información sobre dendrogramas generados
    """
    try:
        req4_dir = settings.BASE_DIR / 'requirement_4'
        
        dendrograms = {
            'ward': req4_dir / 'dendrogram_ward.png',
            'complete': req4_dir / 'dendrogram_complete.png',
            'average': req4_dir / 'dendrogram_average.png'
        }
        
        available = {k: v.exists() for k, v in dendrograms.items()}
        
        if not any(available.values()):
            return Response({
                'error': 'No hay dendrogramas generados',
                'available': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'available': True,
            'dendrograms': available,
            'message': f'{sum(available.values())} dendrogramas disponibles'
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_sorting_results(request):
    """
    GET /api/sorting/results/
    Devuelve archivos de ordenamiento generados
    """
    try:
        processed_dir = settings.DATA_PROCESSED / 'ordenamiento'
        
        if not processed_dir.exists():
            return Response({
                'error': 'No hay resultados de ordenamiento',
                'available': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        bib_files = list(processed_dir.glob('*.bib'))
        
        return Response({
            'available': True,
            'total_files': len(bib_files),
            'files': [{'name': f.name, 'size': f.stat().st_size} for f in bib_files]
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_graph_info(request):
    """
    GET /api/graphs/info/?type=citaciones|terminos
    Devuelve información sobre grafos generados
    """
    try:
        graph_type = request.GET.get('type', 'citaciones')
        grafos_dir = settings.BASE_DIR / 'requirement_grafos'
        
        if graph_type == 'citaciones':
            graph_file = grafos_dir / 'grafos_citaciones.png'
        else:
            graph_file = grafos_dir / 'grafos_terminos.png'
        
        if not graph_file.exists():
            return Response({
                'error': f'Grafo de {graph_type} no encontrado',
                'available': False,
                'path': str(graph_file)
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'available': True,
            'type': graph_type,
            'file': graph_file.name,
            'size': graph_file.stat().st_size
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
