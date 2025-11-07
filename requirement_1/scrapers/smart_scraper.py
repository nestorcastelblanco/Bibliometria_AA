#!/usr/bin/env python3
"""
Smart Scraper - Ejecuta scrapers optimizados de ACM y SAGE
"""
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

def run_scraper(script_name, name):
    """Ejecuta un scraper y retorna su resultado"""
    script_path = PROJECT_ROOT / "requirement_1" / "scrapers" / script_name
    
    print(f"\n{'='*70}")
    print(f"🚀 Ejecutando {name}...")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=False,
            text=True
        )
        success = result.returncode == 0
        if success:
            print(f"✅ {name} completado exitosamente")
        else:
            print(f"⚠️  {name} finalizó con código: {result.returncode}")
        return success
    except Exception as e:
        print(f"❌ Error ejecutando {name}: {e}")
        return False

def smart_scrape_acm():
    """Ejecuta el scraper de ACM optimizado con anti-CAPTCHA"""
    return run_scraper("acm_scraper_undetected.py", "ACM Scraper (Undetected)")

def smart_scrape_sage():
    """Ejecuta el scraper de SAGE optimizado"""
    return run_scraper("sage_undetected.py", "SAGE Scraper (Undetected)")

if __name__ == "__main__":
    print("\n🚀 SCRAPING INTELIGENTE DE DATOS BIBLIOGRÁFICOS")
    print("=" * 70)
    
    # Ejecutar scrapers
    acm_success = smart_scrape_acm()
    sage_success = smart_scrape_sage()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    
    acm_dir = PROJECT_ROOT / "data" / "raw" / "acm"
    sage_dir = PROJECT_ROOT / "data" / "raw" / "sage"
    
    acm_files = list(acm_dir.glob("*.bib")) if acm_dir.exists() else []
    sage_files = list(sage_dir.glob("*.bib")) if sage_dir.exists() else []
    
    print(f"\n📁 ACM:  {len(acm_files):3d} archivos {'✅' if acm_success else '⚠️'}")
    print(f"📁 SAGE: {len(sage_files):3d} archivos {'✅' if sage_success else '⚠️'}")
    print(f"\n📊 TOTAL: {len(acm_files) + len(sage_files)} archivos bibliográficos")
    
    if acm_success and sage_success:
        print("\n✅ Scrapers ejecutados correctamente")
        sys.exit(0)
    elif len(acm_files) > 0 or len(sage_files) > 0:
        print("\n⚠️  Al menos un scraper completó con datos")
        sys.exit(0)
    else:
        print("\n❌ No se obtuvieron datos")
        sys.exit(1)
