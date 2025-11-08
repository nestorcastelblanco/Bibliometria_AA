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
        # Configurar navegador con más argumentos anti-detección
        print("\n🌐 Iniciando Chromium...")
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--allow-running-insecure-content',
                '--disable-ipc-flooding-protection',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-background-timer-throttling',
                '--disable-hang-monitor',
                '--disable-client-side-phishing-detection',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--metrics-recording-only',
                '--no-first-run',
                '--safebrowsing-disable-auto-update',
                '--enable-automation',
                '--password-store=basic',
                '--use-mock-keychain',
            ]
        )
        
        # Configurar contexto del navegador con headers más realistas
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            accept_downloads=True,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        )
        
        # Configurar descargas
        context.on('download', lambda download: handle_download(download, output_dir))
        
        page = context.new_page()
        
        # Inyectar técnicas anti-detección más agresivas
        print("🥷 Aplicando técnicas anti-detección avanzadas...")
        page.add_init_script("""
            // Ocultar webdriver
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Sobrescribir propiedades de detección
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                    {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
                    {name: 'Native Client', filename: 'internal-nacl-plugin', description: 'Native Client Executable'}
                ]
            });
            
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});
            
            // Simular chrome real
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Permisos
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Ocultar automatización
            delete navigator.__proto__.webdriver;
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
                
                # Verificar si es Cloudflare y esperar de forma más inteligente
                title = page.title()
                if "just a moment" in title.lower() or "cloudflare" in title.lower():
                    print(f"   ⚠️  Cloudflare detectado: {title}")
                    print(f"   ⏳ Esperando resolución automática (hasta 30s)...")
                    
                    # Esperar activamente a que desaparezca el challenge
                    try:
                        # Esperar a que aparezca algún elemento característico de ACM
                        page.wait_for_selector(".citation-preview, .search__item, .issue-item", timeout=30000)
                        print(f"   ✅ Cloudflare superado!")
                        time.sleep(2)  # Espera adicional para estabilidad
                    except:
                        print(f"   ❌ Cloudflare no se resolvió en 30s")
                        # Intentar scroll como último recurso
                        try:
                            print(f"   🔄 Intentando scroll como humano...")
                            page.mouse.wheel(0, 300)
                            time.sleep(5)
                            page.mouse.wheel(0, 300)
                            time.sleep(5)
                            
                            title = page.title()
                            if "just a moment" in title.lower():
                                print(f"   ❌ Scroll no ayudó, saltando página")
                                continue
                        except:
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
