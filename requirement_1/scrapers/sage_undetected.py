#!/usr/bin/env python3
"""
SAGE Journals BibTeX Downloader usando undetected-chromedriver
Para evadir Cloudflare y permitir resolución manual de CAPTCHA
"""
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from datetime import datetime
import sys
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAGE_DATA_DIR = PROJECT_ROOT / 'data' / 'raw' / 'sage'
SAGE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Configurar carpeta de descargas
DOWNLOAD_DIR = str(SAGE_DATA_DIR.absolute())

def setup_driver():
    """Configura undetected-chromedriver para evadir Cloudflare"""
    options = uc.ChromeOptions()
    
    # Configurar carpeta de descargas
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Opciones para mayor estabilidad
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    
    # Crear driver con undetected-chromedriver
    try:
        driver = uc.Chrome(options=options, version_main=None)
        print("    ✅ Driver Chrome iniciado correctamente")
        return driver
    except Exception as e:
        print(f"    ❌ Error iniciando Chrome: {e}")
        raise

def wait_for_download(download_dir, initial_files, timeout=30):
    """Espera a que se complete la descarga"""
    print(f"    ⏳ Esperando archivo .bib...")
    seconds = 0
    
    while seconds < timeout:
        time.sleep(1)
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files
        
        # Buscar archivos .bib nuevos que no sean .crdownload
        bib_files = [f for f in new_files if f.endswith('.bib') and not f.endswith('.crdownload')]
        
        # También buscar archivos sage.bib (nombre por defecto)
        sage_files = [f for f in new_files if f == 'sage.bib']
        
        if bib_files or sage_files:
            time.sleep(2)  # Esperar un poco más para asegurar
            return list(bib_files + sage_files)[0]
        
        seconds += 1
    
    # Si no se encontró archivo, revisar si hay archivos temporales
    temp_files = [f for f in os.listdir(download_dir) if f.endswith('.crdownload')]
    if temp_files:
        print(f"    ⚠️  Archivo temporal detectado: {temp_files[0]}")
        print("    ⏳ Esperando que termine la descarga...")
        # Esperar un poco más
        for _ in range(10):
            time.sleep(2)
            if not any(f.endswith('.crdownload') for f in os.listdir(download_dir)):
                current_files = set(os.listdir(download_dir))
                new_files = current_files - initial_files
                bib_files = [f for f in new_files if f.endswith('.bib')]
                if bib_files:
                    return bib_files[0]
    
    return None

def rename_downloaded_file(old_name, page_num):
    """Renombra el archivo descargado"""
    # Queremos el mismo patrón que los archivos existentes en la carpeta
    # Ej: SAGE_Generative_Artificial_Intelligence_page1.bib
    page_index = page_num + 1
    target_name = f"SAGE_Generative_Artificial_Intelligence_page{page_index}.bib"
    old_path = SAGE_DATA_DIR / old_name
    target_path = SAGE_DATA_DIR / target_name

    if not old_path.exists():
        return None

    # Si ya existe el archivo objetivo, eliminamos el descargado temporal
    if target_path.exists():
        try:
            old_path.unlink()
        except Exception:
            pass
        return target_name

    # Renombrar al formato estándar
    try:
        old_path.rename(target_path)
        return target_name
    except Exception:
        # Fallback: añadir timestamp si falla el rename directo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback_name = f"SAGE_Generative_Artificial_Intelligence_page{page_index}_{timestamp}.bib"
        try:
            old_path.rename(SAGE_DATA_DIR / fallback_name)
            return fallback_name
        except Exception:
            return None

def check_if_page_exists(page_num):
    """Verifica si ya existe un archivo para esta página"""
    page_index = page_num + 1
    target_name = f"SAGE_Generative_Artificial_Intelligence_page{page_index}.bib"
    # También considerar variantes con timestamp
    existing_files = [f for f in os.listdir(SAGE_DATA_DIR)
                      if (f == target_name or f.startswith(f"SAGE_Generative_Artificial_Intelligence_page{page_index}_")) and f.endswith('.bib')]
    return len(existing_files) > 0

def download_page_bibtex(driver, page_num, wait, is_first_page=False):
    """Descarga el BibTeX de una página"""
    print(f"\n{'='*80}")
    print(f"📄 PÁGINA {page_num + 1}")
    print(f"{'='*80}")
    
    # URL de la página
    url = f"https://journals.sagepub.com/action/doSearch?AllField=generative+artificial+intelligence&pageSize=20&startPage={page_num}"
    
    print(f"🌐 Navegando a: {url}")
    driver.get(url)
    
    # Esperar carga inicial
    print("    ⏳ Esperando carga inicial...")
    time.sleep(5)
    
    # Solo en la primera página: aceptar cookies y esperar carga automática
    if is_first_page:
        # Intentar aceptar cookies automáticamente
        print("    🍪 Intentando aceptar cookies...")
        try:
            cookie_buttons = [
                "//button[contains(text(), 'Accept Non-Essential Cookies')]",
                "//button[contains(text(), 'Accept All Cookies')]",
                "//button[contains(text(), 'Accept')]",
                "//a[contains(text(), 'Accept Non-Essential Cookies')]",
            ]
            
            cookie_accepted = False
            for selector in cookie_buttons:
                try:
                    cookie_btn = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", cookie_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", cookie_btn)
                    print("    ✅ Cookies aceptadas automáticamente")
                    cookie_accepted = True
                    time.sleep(3)
                    break
                except:
                    continue
            
            if not cookie_accepted:
                print("    ⚠️  No se pudo aceptar cookies automáticamente, continuando...")
        except:
            print("    ⚠️  Modal de cookies no encontrado, continuando...")
        
        # Esperar automáticamente para que la página cargue completamente
        print("    ⏳ Esperando carga automática (15 segundos)...")
        time.sleep(15)
        
        # Verificar si hay elementos de búsqueda cargados
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".issue-item, .search-result, tr")))
            print("    ✅ Resultados de búsqueda detectados")
        except:
            print("    ⚠️  Resultados no detectados, esperando 10 segundos más...")
            time.sleep(10)
        
        print("    ✅ Continuando con descarga automática...")
    else:
        # Páginas 2-5: solo esperar carga, sin pausas
        print("    ⏳ Esperando que carguen los resultados...")
        time.sleep(5)
    
    time.sleep(2)
    
    # Guardar archivos actuales antes de la descarga
    initial_files = set(os.listdir(DOWNLOAD_DIR))
    
    try:
        # 1. Seleccionar todos los artículos
        print("\n1️⃣  Seleccionando todos los artículos...")
        
        select_all_clicked = False
        
        # Método 1: Buscar checkbox "Select all"
        selectors_to_try = [
            "//input[@type='checkbox' and @name='markall']",
            "//input[@type='checkbox' and contains(@id, 'selectAll')]",
            "//input[@type='checkbox' and contains(@class, 'selectAll')]", 
            "//label[contains(text(), 'Select all')]/preceding-sibling::input",
            "//label[contains(text(), 'Select all')]/input",
            "//th//input[@type='checkbox']",  # Checkbox en header de tabla
        ]
        
        for selector in selectors_to_try:
            try:
                select_all = driver.find_element(By.XPATH, selector)
                driver.execute_script("arguments[0].scrollIntoView(true);", select_all)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", select_all)
                print("    ✅ Click en 'Select all'")
                select_all_clicked = True
                time.sleep(2)
                break
            except:
                continue
        
        # Método 2: Seleccionar checkboxes individuales
        if not select_all_clicked:
            print("    ⚠️  'Select all' no encontrado, seleccionando individualmente...")
            try:
                # Buscar checkboxes en diferentes contenedores
                checkbox_selectors = [
                    ".issue-item input[type='checkbox']",
                    ".search-result input[type='checkbox']", 
                    "input[type='checkbox'][name*='articles']",
                    "tr input[type='checkbox']",
                    ".result-item input[type='checkbox']"
                ]
                
                checkboxes = []
                for selector in checkbox_selectors:
                    try:
                        found_boxes = driver.find_elements(By.CSS_SELECTOR, selector)
                        if found_boxes:
                            checkboxes = found_boxes
                            break
                    except:
                        continue
                
                print(f"    📦 Encontrados {len(checkboxes)} checkboxes")
                selected_count = 0
                for checkbox in checkboxes[:20]:
                    try:
                        if not checkbox.is_selected():
                            driver.execute_script("arguments[0].click();", checkbox)
                            selected_count += 1
                    except:
                        pass
                
                if selected_count > 0:
                    print(f"    ✅ {selected_count} artículos seleccionados")
                    time.sleep(2)
                else:
                    print("    ⚠️  No se pudieron seleccionar artículos automáticamente")
                    print("    ⚠️  Esperando 5 segundos y continuando...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
                print("    ⚠️  Esperando 5 segundos y continuando...")
                time.sleep(5)
        
        # 2. Click en "Export selected citations"
        print("\n2️⃣  Haciendo click en 'Export selected citations'...")
        
        export_clicked = False
        export_selectors = [
            "//span[contains(text(), 'Export selected citations')]",
            "//a[contains(text(), 'Export selected citations')]", 
            "//button[contains(text(), 'Export selected citations')]",
            "//a[contains(@class, 'export') and contains(text(), 'Export')]",
        ]
        
        for selector in export_selectors:
            try:
                export_btn = driver.find_element(By.XPATH, selector)
                driver.execute_script("arguments[0].scrollIntoView(true);", export_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", export_btn)
                print("    ✅ Click en 'Export selected citations'")
                export_clicked = True
                time.sleep(3)
                break
            except:
                continue
        
        if not export_clicked:
            print("    ⚠️  No se encontró botón automáticamente")
            print("    ⚠️  Esperando 5 segundos y continuando...")
            time.sleep(5)
        
        # 3. Seleccionar BibTeX del dropdown
        print("\n3️⃣  Seleccionando formato BibTeX del dropdown...")
        
        bibtex_selected = False
        try:
            # Buscar el select por ID
            citation_format_select = driver.find_element(By.ID, "citation-format")
            driver.execute_script("arguments[0].scrollIntoView(true);", citation_format_select)
            time.sleep(1)
            
            # Seleccionar la opción BibTeX
            select = Select(citation_format_select)
            select.select_by_value("bibtex")
            print("    ✅ BibTeX seleccionado del dropdown")
            bibtex_selected = True
            time.sleep(2)
            
        except Exception as e:
            print(f"    ⚠️  Error seleccionando BibTeX: {e}")
            # Métodos alternativos
            bibtex_selectors = [
                "//select[@id='citation-format']//option[@value='bibtex']",
                "//option[@value='bibtex']",
                "//option[contains(text(), 'BibTeX')]",
            ]
            
            for selector in bibtex_selectors:
                try:
                    bibtex_option = driver.find_element(By.XPATH, selector)
                    driver.execute_script("arguments[0].selected = true;", bibtex_option)
                    print("    ✅ BibTeX seleccionado (método alternativo)")
                    bibtex_selected = True
                    time.sleep(1)
                    break
                except:
                    continue
        
        if not bibtex_selected:
            print("    ⚠️  BibTeX no se pudo seleccionar automáticamente")
            print("    ⚠️  Esperando 5 segundos y continuando...")
            time.sleep(5)
        
        # 4. Click en el enlace de descarga que aparece
        print("\n4️⃣  Haciendo click en enlace de descarga...")
        
        download_clicked = False
        # Esperar a que aparezca el enlace de descarga
        time.sleep(2)
        
        download_selectors = [
            "//a[contains(@href, 'data:Application/x-bibtex')]",
            "//a[contains(@class, 'download__btn')]",
            "//a[contains(text(), 'Download citation')]",
            "//button[contains(text(), 'Download Citation')]",
            "//button[contains(text(), 'Download')]",
            "//a[contains(text(), 'Download Citation')]",
            "//input[@type='submit' and contains(@value, 'Download')]",
        ]
        
        for selector in download_selectors:
            try:
                download_btn = driver.find_element(By.XPATH, selector)
                driver.execute_script("arguments[0].scrollIntoView(true);", download_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", download_btn)
                print("    ✅ Click en enlace de descarga")
                download_clicked = True
                break
            except:
                continue
        
        if not download_clicked:
            print("    ⚠️  Enlace de descarga no encontrado automáticamente")
            print("    ⚠️  Esperando 5 segundos y continuando...")
            time.sleep(5)
        
        # 5. Esperar descarga
        print("\n5️⃣  Esperando descarga...")
        downloaded_file = wait_for_download(DOWNLOAD_DIR, initial_files, timeout=30)
        
        if downloaded_file:
            print(f"    ✅ Archivo descargado: {downloaded_file}")
            new_name = rename_downloaded_file(downloaded_file, page_num)
            if new_name:
                file_path = SAGE_DATA_DIR / new_name
                size_kb = file_path.stat().st_size / 1024
                print(f"    ✅ Renombrado a: {new_name} ({size_kb:.1f} KB)")
            return True
        else:
            print("    ⚠️  Timeout esperando descarga")
            print("    ¿Se descargó el archivo? Verifica la carpeta de descargas")
            
            # Verificar si hay archivos nuevos
            current_files = set(os.listdir(DOWNLOAD_DIR))
            new_files = current_files - initial_files
            if new_files:
                print(f"    📦 Archivos nuevos detectados: {new_files}")
                return True
            
            return False
            
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("=" * 80)
    print("🔬 SAGE BibTeX Downloader - Undetected ChromeDriver")
    print("=" * 80)
    print(f"📁 Carpeta de descargas: {DOWNLOAD_DIR}")
    print("=" * 80)
    
    driver = None
    try:
        print("\n🚀 Inicializando Chrome (anti-detección)...")
        driver = setup_driver()
        print("    ✅ Chrome iniciado correctamente")
        
        wait = WebDriverWait(driver, 20)

        # PRUEBA: Procesar solo 2 páginas para testing
        num_pages = 2
        successful_downloads = 0
        
        print(f"\n📋 Iniciando procesamiento de {num_pages} páginas...")
        
        for page_num in range(num_pages):
            try:
                print(f"\n{'='*60}")
                print(f"📄 PROCESANDO PÁGINA {page_num + 1}/{num_pages}")
                print(f"{'='*60}")
                
                # Verificar si ya existe archivo para esta página
                if check_if_page_exists(page_num):
                    print(f"📁 Página {page_num + 1} ya existe, saltando...")
                    successful_downloads += 1
                    continue
                    
                # Solo la primera página requiere interacción manual
                is_first = (page_num == 0)
                success = download_page_bibtex(driver, page_num, wait, is_first_page=is_first)
                
                if success:
                    successful_downloads += 1
                    print(f"✅ Página {page_num + 1}/{num_pages} COMPLETADA")
                else:
                    print(f"⚠️  Página {page_num + 1}/{num_pages} - Error detectado, continuando...")
                
                # Pausa antes de siguiente página
                if page_num < num_pages - 1:
                    print(f"⏭️  Preparando página {page_num + 2}...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ Error en página {page_num + 1}: {e}")
                continue
        
        # Resumen final
        print("\n" + "=" * 80)
        print("📊 RESUMEN FINAL")
        print("=" * 80)
        print(f"✅ Páginas exitosas: {successful_downloads}/{num_pages}")
        
        # Listar archivos descargados
        bib_files = sorted([f for f in os.listdir(DOWNLOAD_DIR)
                          if (f.startswith('SAGE_Generative_Artificial_Intelligence_page') or f.startswith('sage_page')) and f.endswith('.bib')])

        if bib_files:
            print(f"\n📚 Archivos BibTeX descargados ({len(bib_files)}):")
            total_size = 0
            for bib_file in bib_files:
                file_path = SAGE_DATA_DIR / bib_file
                if file_path.exists():
                    size_kb = file_path.stat().st_size / 1024
                    total_size += size_kb
                    print(f"  - {bib_file} ({size_kb:.1f} KB)")
            print(f"\n📦 Tamaño total: {total_size:.1f} KB")
        else:
            print("\n⚠️  No se encontraron archivos BibTeX descargados")

        return successful_downloads > 0
        
    except KeyboardInterrupt:
        print("\n\n🛑 Interrumpido por usuario")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"\n💡 Reintentando en modo seguro...")
        # Intentar cerrar driver si existe
        try:
            if driver:
                driver.quit()
        except:
            pass
        time.sleep(5)
        return False
        
    finally:
        if driver:
            print("\n🔚 Cerrando navegador en 3 segundos...")
            time.sleep(3)
            try:
                driver.quit()
                print("✅ Navegador cerrado correctamente")
            except Exception as e:
                print(f"⚠️  Error cerrando navegador: {e}")

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n🏁 SAGE Scraper terminado - Éxito: {success}")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Error crítico en SAGE Scraper: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
