#!/usr/bin/env python3
"""
ACM Scraper usando Playwright en modo HEADLESS + técnicas anti-detección
Basado en solución exitosa de compañero (Google Cloud + Django + Playwright headless)
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from pathlib import Path
from datetime import datetime
import time
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

def scrape_acm_playwright(max_pages=2, headless=True):
    """
    Scraper de ACM usando Playwright en modo headless
    
    Args:
        max_pages: Número de páginas a scrapear
        headless: Si True, ejecuta sin interfaz gráfica (para servidores)
    """
    download_dir = PROJECT_ROOT / "downloads"
    output_dir = PROJECT_ROOT / "data" / "raw" / "acm"
    download_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("🎭 ACM Scraper con Playwright (Modo Headless)")
    print("=" * 70)
    print(f"Páginas: {max_pages}")
    print(f"Modo headless: {headless}")
    print(f"Salida: {output_dir}")
    print("=" * 70)
    
    downloaded_files = []
    
    with sync_playwright() as p:
        # Configurar navegador
        print("\n🌐 Iniciando Chromium...")
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        # Configurar contexto del navegador
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            accept_downloads=True
        )
        
        # Configurar descargas
        context.on('download', lambda download: handle_download(download, output_dir))
        
        page = context.new_page()
        
        # Inyectar técnicas anti-detección manualmente
        print("🥷 Aplicando técnicas anti-detección...")
        page.add_init_script("""
            // Ocultar webdriver
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Simular chrome
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            
            // Ocultar automation
            window.chrome = {runtime: {}};
        """)
        
        print("✅ Navegador iniciado\n")
        
        try:
            for page_num in range(max_pages):
                print(f"📄 Página {page_num + 1}/{max_pages}")
                
                # URL de búsqueda ACM
                url = f"https://dl.acm.org/action/doSearch?AllField=generative+artificial+intelligence&startPage={page_num}&pageSize=50"
                print(f"   🌐 Navegando a: {url[:80]}...")
                
                # Estrategia más robusta: intentar múltiples veces
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        # Usar 'domcontentloaded' en lugar de 'networkidle' (más rápido)
                        page.goto(url, wait_until='domcontentloaded', timeout=90000)
                        print(f"   ✅ Página cargada")
                        break
                    except PlaywrightTimeout:
                        if retry < max_retries - 1:
                            print(f"   ⏳ Timeout, reintentando ({retry + 1}/{max_retries})...")
                            time.sleep(5)
                        else:
                            print(f"   ❌ No se pudo cargar después de {max_retries} intentos")
                            continue
                
                # Esperar a que carguen los elementos principales
                time.sleep(5)
                
                # Verificar si es Cloudflare
                title = page.title()
                if "just a moment" in title.lower() or "cloudflare" in title.lower():
                    print(f"   ⚠️  Cloudflare detectado: {title}")
                    print(f"   ⏳ Esperando 15s para bypass automático...")
                    time.sleep(15)
                    
                    title = page.title()
                    if "just a moment" in title.lower():
                        print(f"   ❌ Cloudflare no se resolvió automáticamente")
                        continue
                
                print(f"   ✅ Página cargada: {title[:50]}...")
                
                # Aceptar cookies (primera página)
                if page_num == 0:
                    try:
                        print("   🍪 Aceptando cookies...")
                        cookie_btn = page.locator("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
                        if cookie_btn.is_visible(timeout=3000):
                            cookie_btn.click()
                            print("   ✅ Cookies aceptadas")
                            time.sleep(2)
                    except:
                        print("   ⏭️  No se encontró botón de cookies (continuando)")
                
                # Seleccionar todos los resultados
                try:
                    print("   ☑️  Seleccionando resultados...")
                    checkbox = page.locator("input[name='markall']")
                    checkbox.click()
                    time.sleep(2)
                    print("   ✅ Resultados seleccionados")
                except Exception as e:
                    print(f"   ❌ Error seleccionando: {str(e)[:100]}")
                    continue
                
                # Abrir modal de exportación
                try:
                    print("   📤 Abriendo exportación...")
                    export_btn = page.locator("a.export-citation")
                    export_btn.click()
                    time.sleep(5)
                    print("   ✅ Modal abierto")
                except Exception as e:
                    print(f"   ❌ Error en exportación: {str(e)[:100]}")
                    continue
                
                # Descargar BibTeX
                try:
                    print("   💾 Descargando BibTeX...")
                    download_btn = page.locator("a.download__btn[title='Download citation']")
                    
                    # Esperar descarga
                    with page.expect_download(timeout=30000) as download_info:
                        download_btn.click()
                    
                    download = download_info.value
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"ACM_page{page_num}_{timestamp}.bib"
                    filepath = output_dir / filename
                    
                    download.save_as(filepath)
                    print(f"   ✅ Descargado: {filename}")
                    downloaded_files.append(filename)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ❌ Error descargando: {str(e)[:100]}")
                    continue
                
                # Cerrar modal
                try:
                    close_btn = page.locator("i.icon-close_thin")
                    close_btn.click()
                    time.sleep(1)
                except:
                    pass
                
                # Ir a siguiente página (si no es la última)
                if page_num < max_pages - 1:
                    try:
                        print("   ➡️  Siguiente página...")
                        next_btn = page.locator("a.pagination__btn--next")
                        next_btn.click()
                        time.sleep(3)
                    except:
                        print("   ⚠️  No se pudo navegar a siguiente página")
                
                print(f"   ✅ Página {page_num + 1} completada\n")
        
        except Exception as e:
            print(f"\n❌ Error general: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            browser.close()
    
    print("\n" + "=" * 70)
    print(f"✅ Scraping completado: {len(downloaded_files)}/{max_pages} páginas")
    print("=" * 70)
    
    if downloaded_files:
        print("\n📁 Archivos descargados:")
        for f in downloaded_files:
            print(f"   - {f}")
    
    return downloaded_files

def handle_download(download, output_dir):
    """Maneja las descargas automáticas"""
    print(f"   📥 Descarga iniciada: {download.suggested_filename}")

def scrape_acm(max_pages=2):
    """Wrapper para compatibilidad con run_all.py"""
    return scrape_acm_playwright(max_pages=max_pages, headless=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ACM Scraper con Playwright")
    parser.add_argument("--pages", type=int, default=2, help="Número de páginas")
    parser.add_argument("--no-headless", action="store_true", help="Mostrar navegador")
    args = parser.parse_args()
    
    files = scrape_acm_playwright(
        max_pages=args.pages,
        headless=not args.no_headless
    )
    
    print(f"\n📊 Total: {len(files)} archivos")
