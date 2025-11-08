"""
API Views para ejecutar requerimientos interactivamente
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import subprocess
import sys
from pathlib import Path
import json
import pandas as pd


@api_view(['POST'])
def run_req2(request):
    """
    POST /api/req2
    Body: {"indices": [0, 3, 7]}
    """
    try:
        indices = request.data.get('indices', [])
        
        # Ejecutar script de req2
        script = settings.BASE_DIR / 'requirement_2' / 'run_req2.py'
        
        # Construir comando con indices
        cmd = [sys.executable, str(script)]
        if indices:
            cmd.extend(['--indices'] + [str(i) for i in indices])
        
        result = subprocess.run(
            cmd,
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Leer resultados
        csv_file = settings.DATA_PROCESSED / 'reporte_similitud_top.csv'
        md_file = settings.DATA_PROCESSED / 'reporte_similitud.md'
        
        response_data = {
            'ok': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
        # Agregar CSV si existe
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            response_data['table'] = df.head(10).to_dict(orient='records')
        
        # Agregar markdown si existe
        if md_file.exists():
            with open(md_file, 'r', encoding='utf-8') as f:
                response_data['md'] = f.read()
        
        return Response(response_data)
    
    except Exception as e:
        return Response({
            'ok': False,
            'stderr': str(e)
        })


@api_view(['POST'])
def run_req3(request):
    """POST /api/req3"""
    try:
        script = settings.BASE_DIR / 'requirement_3' / 'run_req3.py'
        
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Leer resultados JSON si existe
        json_file = settings.DATA_PROCESSED / 'requirement_3/req3_resultados.json'
        result_data = {}
        
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
        
        return Response({
            'ok': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'result': result_data
        })
    
    except Exception as e:
        return Response({
            'ok': False,
            'stderr': str(e)
        })


@api_view(['POST'])
def run_req4(request):
    """POST /api/req4"""
    try:
        script = settings.BASE_DIR / 'requirement_4' / 'run_req4.py'
        
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return Response({
            'ok': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        })
    
    except Exception as e:
        return Response({
            'ok': False,
            'stderr': str(e)
        })


@api_view(['POST'])
def run_req5(request):
    """POST /api/req5"""
    try:
        script = settings.BASE_DIR / 'requirement_5' / 'run_req5.py'
        
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return Response({
            'ok': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        })
    
    except Exception as e:
        return Response({
            'ok': False,
            'stderr': str(e)
        })


@api_view(['POST'])
def run_grafos_cit(request):
    """POST /api/grafos/cit"""
    try:
        script = settings.BASE_DIR / 'requirement_grafos' / 'run_grafos.py'
        
        result = subprocess.run(
            [sys.executable, str(script), '--tipo', 'citaciones'],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return Response({
            'ok': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        })
    
    except Exception as e:
        return Response({
            'ok': False,
            'stderr': str(e)
        })


@api_view(['POST'])
def run_grafos_terms(request):
    """POST /api/grafos/terms"""
    try:
        script = settings.BASE_DIR / 'requirement_grafos' / 'run_grafos.py'
        
        result = subprocess.run(
            [sys.executable, str(script), '--tipo', 'terminos'],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return Response({
            'ok': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        })
    
    except Exception as e:
        return Response({
            'ok': False,
            'stderr': str(e)
        })


@api_view(['GET'])
def list_assets(request):
    """
    GET /api/list_assets?scope=req2&limit=24
    Lista imágenes y PDFs generados por un requerimiento
    """
    scope = request.GET.get('scope', 'req1')
    limit = int(request.GET.get('limit', 24))
    
    # Mapear scope a directorio
    scope_dirs = {
        'req1': settings.DATA_RAW,
        'req2': settings.DATA_PROCESSED,
        'req3': settings.BASE_DIR / 'requirement_3',
        'req4': settings.BASE_DIR / 'requirement_4',
        'req5': settings.BASE_DIR / 'requirement_5',
        'grafos_cit': settings.BASE_DIR / 'requirement_grafos',
        'grafos_terms': settings.BASE_DIR / 'requirement_grafos',
    }
    
    base_dir = scope_dirs.get(scope, settings.DATA_PROCESSED)
    
    images = []
    pdfs = []
    
    # Buscar imágenes
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        for img in base_dir.rglob(ext):
            rel_path = img.relative_to(settings.BASE_DIR)
            images.append({
                'name': img.name,
                'rel': str(rel_path),
                'bytes': img.stat().st_size
            })
    
    # Buscar PDFs
    for pdf in base_dir.rglob('*.pdf'):
        rel_path = pdf.relative_to(settings.BASE_DIR)
        pdfs.append({
            'name': pdf.name,
            'rel': str(rel_path),
            'bytes': pdf.stat().st_size
        })
    
    return Response({
        'items': {
            'images': images[:limit],
            'pdfs': pdfs[:limit]
        }
    })
