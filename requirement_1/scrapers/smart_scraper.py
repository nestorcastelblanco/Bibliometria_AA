#!/usr/bin/env python3
"""
Smart Scraper - Ejecuta scrapers optimizados de ACM y SAGE
"""
import sys
import subprocess
import time
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
            text=True,
            timeout=600  # 10 minutos timeout
        )
        success = result.returncode == 0
        if success:
            print(f"✅ {name} completado exitosamente")
        else:
            print(f"⚠️  {name} finalizó con código: {result.returncode}")
        return success
    except subprocess.TimeoutExpired:
        print(f"⏱️  {name} excedió el tiempo límite (10 min)")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando {name}: {e}")
        return False

def smart_scrape_acm():
    """Ejecuta el scraper de ACM optimizado con anti-CAPTCHA"""
    return run_scraper("acm_scraper_undetected.py", "ACM Scraper (Undetected)")

def smart_scrape_sage():
    """Ejecuta el scraper de SAGE optimizado con manejo de errores"""
    print("\n🔄 Preparando ejecución de SAGE...")
    print("   🧹 Limpiando memoria...")
    import gc
    gc.collect()
    
    print("   ⏳ Esperando estabilidad del sistema...")
    time.sleep(5)
    
    return run_scraper("sage_undetected.py", "SAGE Scraper (Undetected)")

if __name__ == "__main__":
    print("\n🚀 SCRAPING INTELIGENTE DE DATOS BIBLIOGRÁFICOS")
    print("=" * 70)
    
    # Ejecutar scrapers con pausa entre ellos
    print("\n📋 PASO 1: Ejecutando ACM Scraper")
    acm_success = smart_scrape_acm()
    
    print(f"   🏁 ACM Scraper terminado: {'✅ Éxito' if acm_success else '⚠️ Con errores'}")
    
    # Pausa entre scrapers para liberar recursos
    print("\n⏳ Esperando 15 segundos para liberar recursos...")
    print("   🧹 Liberando memoria y procesos...")
    import gc
    gc.collect()
    time.sleep(15)
    
    print("\n📋 PASO 2: Ejecutando SAGE Scraper")
    sage_success = smart_scrape_sage()
    
    print(f"   🏁 SAGE Scraper terminado: {'✅ Éxito' if sage_success else '⚠️ Con errores'}")
    
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
