"""
API Views - Lee archivos .bib, CSVs y resultados del pipeline
NO usa base de datos - solo archivos del sistema
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.conf import settings
from django.http import FileResponse, Http404
from pathlib import Path
from datetime import datetime
import bibtexparser
import pandas as pd
import json
import os


class PapersViewSet(viewsets.ViewSet):
    """
    API para leer papers desde archivos .bib
    GET /api/papers/ - Lista todos los papers
    GET /api/papers/stats/ - Estadísticas generales
    """
    
    def list(self, request):
        """Lee todos los archivos .bib de data/raw/acm/"""
        try:
            acm_dir = settings.DATA_RAW / 'acm'
            all_papers = []
            
            if not acm_dir.exists():
                return Response({
                    'error': 'Directorio ACM no encontrado',
                    'path': str(acm_dir)
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Leer todos los .bib
            bib_files = list(acm_dir.glob('*.bib'))
            
            for bib_file in bib_files:
                with open(bib_file, 'r', encoding='utf-8') as f:
                    bib_db = bibtexparser.load(f)
                    for entry in bib_db.entries:
                        all_papers.append({
                            'id': entry.get('ID', ''),
                            'title': entry.get('title', ''),
                            'author': entry.get('author', ''),
                            'year': entry.get('year', ''),
                            'journal': entry.get('journal', ''),
                            'abstract': entry.get('abstract', ''),
                            'doi': entry.get('doi', ''),
                            'url': entry.get('url', ''),
                            'keywords': entry.get('keywords', ''),
                            'source_file': bib_file.name
                        })
            
            return Response({
                'count': len(all_papers),
                'files_processed': len(bib_files),
                'papers': all_papers
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas generales de los papers"""
        try:
            acm_dir = settings.DATA_RAW / 'acm'
            
            if not acm_dir.exists():
                return Response({'error': 'No hay datos'}, status=status.HTTP_404_NOT_FOUND)
            
            bib_files = list(acm_dir.glob('*.bib'))
            total_papers = 0
            years = []
            
            for bib_file in bib_files:
                with open(bib_file, 'r', encoding='utf-8') as f:
                    bib_db = bibtexparser.load(f)
                    total_papers += len(bib_db.entries)
                    years.extend([e.get('year', '') for e in bib_db.entries if e.get('year')])
            
            return Response({
                'total_papers': total_papers,
                'total_files': len(bib_files),
                'year_range': f"{min(years) if years else 'N/A'} - {max(years) if years else 'N/A'}",
                'unique_years': len(set(years))
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimilarityViewSet(viewsets.ViewSet):
    """
    API para resultados de similitud textual (Req2)
    GET /api/similarity/ - Lee resultados de Req2
    """
    
    def list(self, request):
        """Lee resultados de similitud del pipeline"""
        try:
            # Buscar archivos CSV de similitud en data/processed
            processed_dir = settings.DATA_PROCESSED
            similarity_files = list(processed_dir.glob('*similitud*.csv'))
            
            if not similarity_files:
                return Response({
                    'message': 'No hay resultados de similitud. Ejecuta el análisis primero.',
                    'files': []
                }, status=status.HTTP_404_NOT_FOUND)
            
            results = []
            for csv_file in similarity_files:
                df = pd.read_csv(csv_file)
                results.append({
                    'file': csv_file.name,
                    'data': df.to_dict(orient='records'),
                    'shape': df.shape
                })
            
            return Response({
                'count': len(results),
                'results': results
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FrequenciesViewSet(viewsets.ViewSet):
    """
    API para frecuencias y términos asociados (Req3)
    GET /api/frequencies/ - Lee resultados de Req3
    """
    
    def list(self, request):
        """Lee resultados de frecuencias"""
        try:
            processed_dir = settings.DATA_PROCESSED
            freq_files = list(processed_dir.glob('*frecuencia*.csv')) + \
                        list(processed_dir.glob('*terminos*.csv'))
            
            if not freq_files:
                return Response({
                    'message': 'No hay resultados de frecuencias',
                    'files': []
                }, status=status.HTTP_404_NOT_FOUND)
            
            results = []
            for csv_file in freq_files:
                df = pd.read_csv(csv_file)
                results.append({
                    'file': csv_file.name,
                    'data': df.to_dict(orient='records'),
                    'columns': list(df.columns)
                })
            
            return Response({
                'count': len(results),
                'results': results
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClustersViewSet(viewsets.ViewSet):
    """
    API para clustering jerárquico (Req4)
    GET /api/clusters/ - Lee resultados de Req4
    """
    
    def list(self, request):
        """Lee resultados de clustering"""
        try:
            processed_dir = settings.DATA_PROCESSED
            cluster_files = list(processed_dir.glob('*cluster*.csv')) + \
                           list(processed_dir.glob('*dendrograma*.png'))
            
            if not cluster_files:
                return Response({
                    'message': 'No hay resultados de clustering',
                    'files': []
                }, status=status.HTTP_404_NOT_FOUND)
            
            results = {
                'csv_files': [],
                'dendrograms': []
            }
            
            for file in cluster_files:
                if file.suffix == '.csv':
                    df = pd.read_csv(file)
                    results['csv_files'].append({
                        'file': file.name,
                        'data': df.to_dict(orient='records')
                    })
                elif file.suffix == '.png':
                    results['dendrograms'].append({
                        'file': file.name,
                        'path': f'/api/visualizations/{file.name}'
                    })
            
            return Response(results)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def visualizations_view(request, filename):
    """
    Sirve archivos de visualización (imágenes, PDFs)
    GET /api/visualizations/<filename>
    """
    try:
        # Buscar archivo en data/processed
        file_path = settings.DATA_PROCESSED / filename
        
        if not file_path.exists():
            raise Http404(f"Archivo {filename} no encontrado")
        
        return FileResponse(open(file_path, 'rb'))
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def trigger_scraper_view(request):
    """
    Trigger para ejecutar scraper
    POST /api/trigger-scrape/
    Body: {"pages": 5, "headless": true}
    """
    try:
        import subprocess
        from scraper_app.logger import ScraperLogger
        
        pages = request.data.get('pages', 2)
        headless = request.data.get('headless', True)
        
        # Registrar inicio
        logger = ScraperLogger()
        logger.start('scraper', {'pages': pages, 'headless': headless})
        
        cmd = ['python3', 'manage.py', 'run_scraper', '--pages', str(pages)]
        if not headless:
            cmd.append('--no-headless')
        
        # Ejecutar en background (no bloqueante)
        process = subprocess.Popen(
            cmd,
            cwd=settings.BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return Response({
            'status': 'started',
            'message': f'Scraper iniciado con {pages} páginas',
            'pid': process.pid,
            'check_status_at': '/api/scraper-status/'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def scraper_status_view(request):
    """
    Obtener estado del scraper
    GET /api/scraper-status/
    """
    try:
        from scraper_app.logger import ScraperLogger
        from pathlib import Path
        
        logger = ScraperLogger()
        status_data = logger.get_status()
        
        # Agregar info de archivos descargados
        acm_dir = settings.DATA_RAW / 'acm'
        if acm_dir.exists():
            bib_files = list(acm_dir.glob('*.bib'))
            status_data['files_count'] = len(bib_files)
            
            # Archivos más recientes
            if bib_files:
                recent_files = sorted(bib_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
                status_data['recent_files'] = [
                    {
                        'name': f.name,
                        'size': f.stat().st_size,
                        'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                    }
                    for f in recent_files
                ]
        
        return Response(status_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def trigger_analysis_view(request):
    """
    Trigger para ejecutar análisis completo
    POST /api/trigger-analysis/
    Body: {"req2": [0,3,7], "req4n": 25}
    """
    try:
        import subprocess
        
        req2 = request.data.get('req2', [0, 3, 7])
        req4n = request.data.get('req4n', 25)
        
        cmd = [
            'python3', 'manage.py', 'run_analysis',
            '--req2', *[str(i) for i in req2],
            '--req4n', str(req4n)
        ]
        
        # Ejecutar en background
        process = subprocess.Popen(
            cmd,
            cwd=settings.BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return Response({
            'status': 'started',
            'message': 'Análisis iniciado',
            'pid': process.pid
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

