#!/usr/bin/env python3
"""
Script de prueba para verificar scrapers en modo headless.
Crea un directorio temporal y ejecuta los scrapers con límite de 1 página.
"""
import sys
from pathlib import Path
import tempfile
import shutil

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from requirement_1.scrapers.acm_scraper import fetch_acm_articles
from requirement_1.scrapers.sage_scraper import fetch_sage_bibtex

def test_acm_scraper():
    """Prueba el scraper de ACM en modo headless"""
    print("\n" + "="*70)
    print("PRUEBA: ACM Scraper en modo headless")
    print("="*70)
    
    # Crear directorio temporal
    temp_dir = Path(tempfile.mkdtemp())
    output_dir = temp_dir / "acm"
    
    try:
        fetch_acm_articles(
            query="artificial intelligence",
            headless=True,
            user_data_dir=None,  # Sin perfil
            output_dir=str(output_dir),
            page_size=10,
            max_pages=1  # Solo 1 página para prueba rápida
        )
        
        # Verificar resultados
        bib_files = list(output_dir.glob("*.bib"))
        if bib_files:
            print(f"\n✅ ACM Scraper EXITOSO: {len(bib_files)} archivo(s) generado(s)")
            for f in bib_files:
                print(f"   - {f.name} ({f.stat().st_size} bytes)")
            return True
        else:
            print("\n❌ ACM Scraper FALLÓ: No se generaron archivos .bib")
            return False
    finally:
        # Limpiar
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_sage_scraper():
    """Prueba el scraper de SAGE en modo headless"""
    print("\n" + "="*70)
    print("PRUEBA: SAGE Scraper en modo headless")
    print("="*70)
    
    # Crear directorio temporal
    temp_dir = Path(tempfile.mkdtemp())
    output_dir = temp_dir / "sage"
    
    try:
        fetch_sage_bibtex(
            query="artificial intelligence",
            output_dir=str(output_dir),
            headless=True,
            user_data_dir=None,  # Sin perfil
        )
        
        # Verificar resultados
        bib_files = list(output_dir.glob("*.bib"))
        if bib_files:
            print(f"\n✅ SAGE Scraper EXITOSO: {len(bib_files)} archivo(s) generado(s)")
            for f in bib_files:
                print(f"   - {f.name} ({f.stat().st_size} bytes)")
            return True
        else:
            print("\n❌ SAGE Scraper FALLÓ: No se generaron archivos .bib")
            return False
    finally:
        # Limpiar
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("\n" + "🔍 VERIFICACIÓN DE SCRAPERS EN MODO HEADLESS " + "🔍".center(50))
    print("\nEsta prueba verifica que los scrapers funcionen correctamente")
    print("en modo headless (sin interfaz) como se requiere en despliegue.\n")
    
    results = {
        "ACM": test_acm_scraper(),
        "SAGE": test_sage_scraper()
    }
    
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    for scraper, success in results.items():
        status = "✅ EXITOSO" if success else "❌ FALLIDO"
        print(f"{scraper:10s}: {status}")
    
    # Retornar código de salida apropiado
    sys.exit(0 if all(results.values()) else 1)
