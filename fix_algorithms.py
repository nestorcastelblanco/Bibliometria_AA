#!/usr/bin/env python3
"""
Script para arreglar las rutas hardcodeadas de Windows en los algoritmos de ordenamiento
"""
import os
import re
from pathlib import Path

# Directorio de algoritmos
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALGO_DIR = PROJECT_ROOT / "data" / "processed" / "algoritmos_ordenamiento"

def fix_file(file_path):
    """Arregla las rutas en un archivo de algoritmo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Agregar imports necesarios al inicio
    if 'from pathlib import Path' not in content:
        content = content.replace(
            'import os',
            'import os\nfrom pathlib import Path'
        )
    
    # Agregar PROJECT_ROOT
    if 'PROJECT_ROOT =' not in content:
        content = content.replace(
            'from pathlib import Path',
            'from pathlib import Path\n\n# Configurar rutas multiplataforma\nPROJECT_ROOT = Path(__file__).resolve().parents[3]'
        )
    
    # Reemplazar rutas hardcodeadas
    patterns = [
        (r'input_file = r"C:\\Bibliometria\\data\\processed\\productos_unificados\.bib"',
         'input_file = PROJECT_ROOT / "data" / "processed" / "productos_unificados.bib"'),
        (r'output_dir = r"C:\\Bibliometria\\data\\processed\\ordenamiento"',
         'output_dir = PROJECT_ROOT / "data" / "processed" / "ordenamiento"'),
        (r'os\.makedirs\(output_dir, exist_ok=True\)',
         'output_dir.mkdir(parents=True, exist_ok=True)'),
        (r'os\.path\.join\(output_dir, "([^"]+)"\)',
         r'output_dir / "\1"'),
        (r'os\.path\.exists\(input_file\)',
         'input_file.exists()'),
        (r'parse_bib_file\(input_file\)',
         'parse_bib_file(str(input_file))'),
        (r'save_bib\(([^,]+), output_file\)',
         r'save_bib(\1, str(output_file))')
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Escribir el archivo arreglado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Arreglado: {file_path.name}")

def main():
    """Arregla todos los archivos de algoritmos"""
    print("🔧 Arreglando rutas de algoritmos de ordenamiento...")
    
    for py_file in ALGO_DIR.glob("*.py"):
        fix_file(py_file)
    
    print(f"\n✅ Todos los algoritmos arreglados en: {ALGO_DIR}")

if __name__ == "__main__":
    main()