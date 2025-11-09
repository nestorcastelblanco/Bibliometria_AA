"""
API Views para ejecutar requerimientos interactivamente
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import subprocess
import sys
import os
from pathlib import Path
import json
import pandas as pd


@api_view(['POST'])
def run_req2(request):
    """
    POST /api/req2
    Body: {"indices": "0,3,7"} o {"indices": [0, 3, 7]}
    """
    try:
        # Parsear indices del input
        indices_str = request.data.get('indices', '')
        if isinstance(indices_str, str):
            indices = [int(x.strip()) for x in indices_str.split(',') if x.strip()]
        else:
            indices = indices_str
        
        if not indices or len(indices) < 2:
            return Response({
                'ok': False,
                'stderr': 'Se requieren al menos 2 índices. Ejemplo: 0,3,7'
            })
        
        # Importar y ejecutar directamente el módulo
        import sys
        sys.path.insert(0, str(settings.BASE_DIR))
        
        from requirement_2 import run_similarity, reports
        
        # Ejecutar cálculo
        output_json = run_similarity.run(indices)
        
        # Leer JSON de resultados
        with open(output_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Detectar algoritmo principal
        algo = reports._detect_primary_algo(data.get('results', []), prefer=None)
        
        # Generar CSV top 50
        csv_file = settings.DATA_PROCESSED / 'reporte_similitud_top.csv'
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        reports.generate_csv_top(data, algo, top=50, out_csv=csv_file)
        
        # Generar markdown
        md_file = settings.DATA_PROCESSED / 'reporte_similitud.md'
        reports.generate_markdown(data, algo, top=10, out_md=md_file)
        
        # Generar resumen de consola como string
        import io
        from contextlib import redirect_stdout
        
        f_out = io.StringIO()
        with redirect_stdout(f_out):
            reports.print_console_summary(data, algo, top=10)
        console_output = f_out.getvalue()
        
        response_data = {
            'ok': True,
            'stdout': console_output or 'Similitud calculada exitosamente'
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
        import traceback
        return Response({
            'ok': False,
            'stderr': f'{str(e)}\n\n{traceback.format_exc()}'
        })


@api_view(['POST'])
def run_req3(request):
    """POST /api/req3"""
    try:
        script = settings.BASE_DIR / 'requirement_3' / 'run_req3.py'
        
        # Añadir PYTHONPATH para imports relativos
        env = os.environ.copy()
        env['PYTHONPATH'] = str(settings.BASE_DIR)
        
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300,
            env=env
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
        
        # Añadir PYTHONPATH para imports relativos
        env = os.environ.copy()
        env['PYTHONPATH'] = str(settings.BASE_DIR)
        
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300,
            env=env
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
        
        # Añadir PYTHONPATH para imports relativos
        env = os.environ.copy()
        env['PYTHONPATH'] = str(settings.BASE_DIR)
        
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300,
            env=env
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
        
        # Añadir PYTHONPATH para imports relativos
        env = os.environ.copy()
        env['PYTHONPATH'] = str(settings.BASE_DIR)
        
        result = subprocess.run(
            [sys.executable, str(script), 'cit', '--plot'],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300,
            env=env
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
        
        # Borrar PNG anterior para forzar regeneración
        old_png = settings.BASE_DIR / 'requirement_grafos' / 'grafos_terminos.png'
        if old_png.exists():
            old_png.unlink()
        
        # Añadir PYTHONPATH para imports relativos
        env = os.environ.copy()
        env['PYTHONPATH'] = str(settings.BASE_DIR)
        
        # Usar términos de req3 si existe
        terms_file = settings.DATA_PROCESSED / 'términos_grafos.json'
        
        cmd = [sys.executable, str(script), 'terms', '--plot', 
               '--max-nodes', '30',  # Reducir a 30 nodos para legibilidad
               '--min-cooc', '3']     # Mínimo 3 co-ocurrencias
        
        # Si existe archivo de términos, usarlo
        if terms_file.exists():
            cmd.extend(['--terms', str(terms_file)])
        
        result = subprocess.run(
            cmd,
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            timeout=300,
            env=env
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
