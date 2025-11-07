#!/usr/bin/env python3
"""
ACM Scraper usando undetected-chromedriver para evadir CAPTCHA
Descarga archivos BibTeX usando la funcionalidad nativa de ACM
"""
import time
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Detectar si estamos en producción
IS_PRODUCTION = os.environ.get('ENVIRONMENT', 'development') == 'production'

def setup_driver():
    """Configura undetected-chromedriver para evadir CAPTCHA/Cloudflare"""
    # Configurar directorio de descarga
    download_dir = PROJECT_ROOT / 'data' / 'raw' / 'acm'
    download_dir.mkdir(parents=True, exist_ok=True)
    
    options = uc.ChromeOptions()
    
    # Configuraciones base
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Configuraciones específicas para producción (headless)
    if IS_PRODUCTION:
        print("   🔧 Modo PRODUCCIÓN detectado - usando headless mode")
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
    else:
        print("   🔧 Modo DESARROLLO - usando ventana visible")
        options.add_argument('--start-maximized')
    
    # Configurar directorio de descarga
    prefs = {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Crear driver con undetected-chromedriver
    driver = uc.Chrome(options=options, version_main=None)
    
    # Script para ocultar propiedades de webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def download_page_bibtex(driver, page_num):
    """Descarga BibTeX usando la funcionalidad nativa de ACM"""
    try:
        print("   🔍 Esperando que cargue la página...")
        
        # Esperar a que aparezcan los resultados
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".issue-item"))
        )
        time.sleep(3)
        
        print("   ☑️  Seleccionando 'Select All'...")
        
        # Buscar y hacer clic en Select All
        select_all_selectors = [
            "input[name='markall']",
            ".item-results__checkbox input[type='checkbox']",
            "label.checkbox--primary input[type='checkbox']"
        ]
        
        select_all_clicked = False
        for selector in select_all_selectors:
            try:
                select_all_checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                driver.execute_script("arguments[0].click();", select_all_checkbox)
                print("   ✓ Select All activado")
                select_all_clicked = True
                time.sleep(2)
                break
            except Exception as e:
                print(f"   ⚠️  Selector {selector} falló: {str(e)[:50]}")
                continue
        
        if not select_all_clicked:
            print("   ❌ No se pudo activar Select All")
            return False
        
        print("   📤 Haciendo clic en 'Export Citations'...")
        
        # Buscar y hacer clic en Export Citations
        export_selectors = [
            "a.export-citation",
            ".btn.light.export-citation",
            "[title='Export Citations']",
            "[data-target='#exportCitation']"
        ]
        
        export_clicked = False
        for selector in export_selectors:
            try:
                export_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                driver.execute_script("arguments[0].click();", export_btn)
                print("   ✓ Export Citations clickeado")
                export_clicked = True
                time.sleep(3)
                break
            except Exception as e:
                print(f"   ⚠️  Selector {selector} falló: {str(e)[:50]}")
                continue
        
        if not export_clicked:
            print("   ❌ No se pudo hacer clic en Export Citations")
            return False
        
        print("   💾 Buscando botón de descarga...")
        
        # Buscar y hacer clic en el botón de descarga
        download_selectors = [
            "a.download__btn",
            "[title='Download citation']",
            ".icon-Icon_Download",
            "a[role='menuitem'][title='Download citation']"
        ]
        
        download_clicked = False
        for selector in download_selectors:
            try:
                download_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                driver.execute_script("arguments[0].click();", download_btn)
                print("   ✓ Descarga iniciada")
                download_clicked = True
                time.sleep(5)  # Esperar a que termine la descarga
                break
            except Exception as e:
                print(f"   ⚠️  Selector {selector} falló: {str(e)[:50]}")
                continue
        
        if not download_clicked:
            print("   ❌ No se pudo hacer clic en descargar")
            return False
        
        # Renombrar archivo descargado
        download_dir = PROJECT_ROOT / 'data' / 'raw' / 'acm'
        target_filename = f"ACM_generative_artificial_intelligence_page{page_num}.bib"
        
        # Buscar archivo recién descargado
        time.sleep(3)
        downloaded_files = list(download_dir.glob("*.bib"))
        if downloaded_files:
            # Ordenar por fecha de modificación (más reciente primero)
            latest_file = max(downloaded_files, key=lambda f: f.stat().st_mtime)
            target_path = download_dir / target_filename
            
            # Si ya existe, eliminarlo
            if target_path.exists():
                target_path.unlink()
            
            # Renombrar
            latest_file.rename(target_path)
            print(f"   ✅ Archivo renombrado a: {target_filename}")
            return True
        else:
            print("   ❌ No se encontró archivo descargado")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en descarga: {str(e)[:100]}")
        return False

def scrape_acm(max_pages=None):
    """Scraper principal de ACM con undetected-chromedriver usando descarga nativa"""
    
    # PRUEBA: Solo 2 páginas para testing
    if max_pages is None:
        max_pages = 2
    
    print("=" * 70)
    print("🔍 ACM Scraper con Descarga Nativa BibTeX (Anti-CAPTCHA)")
    print("=" * 70)
    print(f"Páginas: {max_pages} (MODO PRUEBA)")
    print(f"Resultados por página: 50")
    print(f"Salida: {PROJECT_ROOT}/data/raw/acm")
    print("=" * 70)
    
    output_dir = PROJECT_ROOT / 'data' / 'raw' / 'acm'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded_files = []
    
    print(f"\n🚀 Iniciando Chrome con anti-detección...")
    driver = setup_driver()
    
    try:
        for page_num in range(max_pages):
            print(f"\n📄 Página {page_num+1}/{max_pages}")
            
            # Construir URL con paginación correcta
            url = f"https://dl.acm.org/action/doSearch?AllField=generative+artificial+intelligence&pageSize=50&startPage={page_num}"
            print(f"   URL: {url}")
            
            # Navegar a la página
            driver.get(url)
            
            # Manejar cookies solo en la primera página
            if page_num == 0:
                print("   🍪 Manejando cookies...")
                time.sleep(3)
                try:
                    selectors = [
                        "//button[contains(text(), 'Allow all cookies')]",
                        "//button[contains(text(), 'Accept')]",
                        "//button[contains(text(), 'AGREE')]",
                        "//button[@id='onetrust-accept-btn-handler']"
                    ]
                    
                    for selector in selectors:
                        try:
                            cookie_btn = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            cookie_btn.click()
                            print("   ✓ Cookies aceptadas")
                            time.sleep(2)
                            break
                        except:
                            continue
                except:
                    print("   ⚠️  No se encontraron cookies")
            
            # Esperar más tiempo en la primera página por posible CAPTCHA
            wait_time = 15 if page_num == 0 else 8
            print(f"   ⏳ Esperando {wait_time}s (CAPTCHA/carga)...")
            time.sleep(wait_time)
            
            # Verificar si hay resultados en la página
            try:
                # Buscar elementos que indican resultados
                results = driver.find_elements(By.CSS_SELECTOR, ".issue-item")
                if not results:
                    print(f"   🏁 No hay más resultados en la página {page_num+1}. Finalizando...")
                    break
                print(f"   📊 Encontrados {len(results)} resultados en esta página")
            except:
                print(f"   ❌ Error verificando resultados en página {page_num+1}")
                break
            
            # Descargar BibTeX de la página
            print("   📥 Descargando BibTeX...")
            success = download_page_bibtex(driver, page_num + 1)
            
            if success:
                filename = f"ACM_generative_artificial_intelligence_page{page_num + 1}.bib"
                downloaded_files.append(filename)
                print(f"   ✅ Página {page_num+1} descargada: {filename}")
            else:
                print(f"   ❌ Error descargando página {page_num+1}")
                # Si hay muchos errores consecutivos, puede que hayamos llegado al final
                continue
        
        # Resumen final
        if downloaded_files:
            print(f"\n🎉 COMPLETADO!")
            print(f"   📊 Páginas descargadas: {len(downloaded_files)}")
            print(f"   📁 Archivos BibTeX:")
            for filename in downloaded_files:
                print(f"      - {filename}")
        else:
            print(f"\n❌ No se descargaron archivos")
    
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrumpido por usuario")
        if downloaded_files:
            print(f"   📁 Archivos descargados hasta ahora:")
            for filename in downloaded_files:
                print(f"      - {filename}")
    
    except Exception as e:
        print(f"\n❌ Error general: {str(e)}")
    
    finally:
        print(f"\n🔚 Cerrando navegador ACM...")
        try:
            if driver:
                driver.quit()
                print("   ✅ Navegador ACM cerrado correctamente")
        except Exception as e:
            print(f"   ⚠️  Error cerrando navegador ACM: {e}")
        
        # Pausa para asegurar limpieza de recursos
        time.sleep(3)
        print("   🧹 Recursos liberados")

if __name__ == "__main__":
    # PRUEBA: Procesar solo 2 páginas para testing
    scrape_acm(max_pages=2)