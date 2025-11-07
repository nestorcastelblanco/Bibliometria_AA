"""
Scraper automatizado para descarga de artículos desde ACM Digital Library.

Implementa web scraping con Selenium y undetected-chromedriver para:
- Realizar búsquedas en ACM Digital Library
- Navegar por páginas de resultados
- Seleccionar artículos automáticamente
- Exportar referencias en formato BibTeX
- Guardar metadata en CSV

Características:
- Soporte para sesiones autenticadas (perfil de Chrome)
- Modo headless para ejecución en background
- Manejo robusto de elementos dinámicos
- Descarga directa de BibTeX sin archivos temporales
- Logs de error para debugging
- Límite configurable de páginas

Parte del Requerimiento 1: Scraping de bibliografía académica.
"""
import os
import time
import csv
import re
import urllib.parse
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ruta relativa multiplataforma
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_total_pages(driver, page_size):
    """
    Determina el número total de páginas de resultados en ACM.
    
    Intenta dos estrategias:
    1. Leer span.hitsLength con total de resultados
    2. Buscar números en enlaces de paginación
    
    Args:
        driver: WebDriver de Selenium activo
        page_size (int): Número de resultados por página
    
    Returns:
        Optional[int]: Número total de páginas (1-indexed) o None si no se puede determinar
    
    Estrategia 1 - Cálculo desde total:
        - Lee elemento span.hitsLength
        - Extrae número total de artículos
        - Calcula páginas: ceil(total / page_size)
    
    Estrategia 2 - Desde paginación:
        - Lee enlaces en ul.pagination__list
        - Extrae números de text, aria-label, title
        - Retorna el máximo
    
    Example:
        >>> pages = get_total_pages(driver, 50)
        >>> pages
        12  # 600 artículos / 50 por página
    
    Notas:
        - Intenta estrategia 1 primero (más confiable)
        - Fallback a estrategia 2 si falla
        - Retorna None si ambas fallan
        - Útil para determinar alcance de scraping
    """
    """Determina el número total de páginas (1-based)."""
    try:
        hits_elem = driver.find_element(By.CSS_SELECTOR, "span.hitsLength")
        hits_text = hits_elem.text.strip().replace(",", "")
        if hits_text.isdigit():
            total_items = int(hits_text)
            return (total_items + page_size - 1) // page_size
    except:
        pass

    try:
        anchors = driver.find_elements(By.CSS_SELECTOR, "ul.pagination__list li a")
        nums = []
        for a in anchors:
            for val in (a.text, a.get_attribute("aria-label"), a.get_attribute("title")):
                if val:
                    found = re.findall(r"\d+", val)
                    nums.extend(int(x) for x in found)
        if nums:
            return max(nums)
    except:
        pass

    return None


def wait_for_results(driver, timeout=15):
    """
    Espera a que carguen los resultados de búsqueda en la página.
    
    Prueba múltiples selectores CSS comunes para detectar cuando
    los resultados están listos para interactuar.
    
    Args:
        driver: WebDriver de Selenium activo
        timeout (int, optional): Segundos máximos de espera. Default: 15
    
    Returns:
        bool: True si se detectaron resultados, False si timeout
    
    Selectores intentados:
        - "h5.issue-item__title a": Títulos de artículos
        - "div.search-results": Contenedor de resultados
        - "section.search-results": Sección de resultados
    
    Example:
        >>> driver.get("https://dl.acm.org/action/doSearch?...")
        >>> success = wait_for_results(driver, timeout=20)
        >>> if success:
        ...     # Procesar resultados
    
    Notas:
        - Intenta cada selector secuencialmente
        - Retorna True al primer match exitoso
        - Útil para manejar carga dinámica de JavaScript
        - Previene errores de elementos no encontrados
    """
    """Espera a que carguen los resultados de artículos."""
    selectors = [
        "h5.issue-item__title a",
        "div.search-results",
        "section.search-results"
    ]
    for sel in selectors:
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel))
            )
            return True
        except:
            continue
    return False


def fetch_acm_articles(query, headless=False, user_data_dir=None, profile_dir="Default",
                       output_dir="data/raw/acm", page_size=50, max_pages=100):
    """
    Automatiza descarga masiva de artículos desde ACM Digital Library.
    
    Pipeline completo de scraping:
    1. Configura Chrome con perfil (para autenticación)
    2. Realiza búsqueda en ACM con query
    3. Detecta número total de páginas
    4. Para cada página:
       a. Navega a la página
       b. Selecciona todos los artículos
       c. Exporta referencias en BibTeX
       d. Descarga BibTeX desde data:// URI
       e. Guarda CSV con títulos y enlaces
    5. Cierra navegador y reporta resultados
    
    Args:
        query (str): Término de búsqueda (ej: "machine learning")
        headless (bool, optional): Ejecutar sin interfaz gráfica. Default: False
        user_data_dir (str, optional): Directorio de perfil de Chrome para sesión.
                                      Útil si requiere autenticación. Default: None
        profile_dir (str, optional): Nombre del perfil dentro de user_data_dir.
                                    Default: "Default"
        output_dir (str, optional): Directorio donde guardar archivos.
                                   Default: "data/raw/acm"
        page_size (int, optional): Resultados por página. Default: 50
        max_pages (int, optional): Máximo de páginas a procesar.
                                  0 = todas las páginas. Default: 100
    
    Archivos generados por página:
        - ACM_{query}_page{N}.bib: Referencias BibTeX
        - {query}_page{N}.csv: Tabla con títulos y enlaces
        - ACM_{query}_page{N}_ERROR.html: Log si falla descarga (debugging)
    
    Process detallado:
        1. Crea directorio de salida si no existe
        2. Configura ChromeOptions con perfil y headless
        3. Inicializa undetected_chromedriver
        4. Construye URL de búsqueda ACM con query encoded
        5. Navega a página inicial y detecta total de páginas
        6. Limita a max_pages si es > 0
        7. Para cada página:
           - Navega con startPage=(página-1)
           - Espera carga de resultados
           - Click en checkbox "marcar todos"
           - Click en botón "Export Citation"
           - Espera modal de exportación
           - Selecciona formato BibTeX en dropdown
           - Click en botón de descarga
           - Extrae contenido desde data:// href
           - Decodifica URL y guarda .bib
           - Extrae títulos de h5.issue-item__title
           - Guarda CSV con títulos y enlaces
        8. Cierra driver en finally
    
    Manejo de errores:
        - Intenta seleccionar todos pero continúa si falla
        - Si modal no abre, skip página
        - Si descarga BibTeX falla, guarda HTML para debug
        - Continúa con siguiente página ante errores
        - Always ejecuta driver.quit() en finally
    
    Example:
        >>> fetch_acm_articles(
        ...     query="artificial intelligence",
        ...     headless=True,
        ...     output_dir="./downloads/acm",
        ...     page_size=50,
        ...     max_pages=5
        ... )
        [ACM] Iniciando búsqueda: artificial intelligence
        [ACM] Se procesarán 5 páginas
        [ACM] Procesando página 1/5...
        [ACM] BibTeX guardado: ./downloads/acm/ACM_artificial_intelligence_page1.bib
        [ACM] CSV guardado: ./downloads/acm/artificial_intelligence_page1.csv
        ...
        [ACM] Proceso finalizado.
    
    Requisitos:
        - undetected_chromedriver instalado
        - Chrome/Chromium instalado
        - Conexión a internet
        - Opcionalmente: sesión ACM autenticada (para acceso completo)
    
    Notas:
        - max_pages=0 descarga TODO (puede ser muy largo)
        - page_size máximo en ACM es típicamente 50-100
        - user_data_dir útil para mantener sesión entre ejecuciones
        - Guarda HTML de error para debugging de problemas
        - Incluye sleeps para evitar rate limiting
        - Usa JavaScript click para evitar interceptación
    """
    print(f"[ACM] Iniciando búsqueda: {query}")
    os.makedirs(output_dir, exist_ok=True)

    options = uc.ChromeOptions()
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument(f"--profile-directory={profile_dir}")
    if headless:
        options.add_argument("--headless=new")
        # Opciones adicionales para modo headless más estable
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
    
    # Configurar user agent para evitar bloqueos
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = uc.Chrome(options=options, use_subprocess=True)
    driver.set_page_load_timeout(300)

    try:
        q = urllib.parse.quote_plus(query)
        base_search = f"https://dl.acm.org/action/doSearch?AllField={q}&pageSize={page_size}&startPage="

        driver.get(base_search + "0")
        wait_for_results(driver, timeout=20)
        time.sleep(2)

        last_page = get_total_pages(driver, page_size)
        if not last_page:
            last_page = 1

        if max_pages > 0:
            last_page = min(last_page, max_pages)

        print(f"[ACM] Se procesarán {last_page} páginas")

        for page in range(1, last_page + 1):
            print(f"[ACM] Procesando página {page}/{last_page}...")
            driver.get(base_search + str(page - 1))
            wait_for_results(driver, timeout=20)
            time.sleep(1)

            try:
                select_all = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='markall']"))
                )
                driver.execute_script("arguments[0].click();", select_all)
                time.sleep(0.5)
            except:
                print("[ACM] No se pudo seleccionar todos los artículos, se continúa...")

            try:
                export_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.export-citation"))
                )
                driver.execute_script("arguments[0].click();", export_btn)
                time.sleep(2)
            except:
                print("[ACM] No se pudo abrir el modal de exportación, se continúa...")
                continue

            try:
                modal = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal__dialog"))
                )
                select = modal.find_element(By.ID, "citation-format")
                for option in select.find_elements(By.TAG_NAME, "option"):
                    if option.get_attribute("value") == "bibtex":
                        option.click()
                        break
                time.sleep(1)

                download_btn = modal.find_element(By.CSS_SELECTOR, "a.download__btn")
                driver.execute_script("arguments[0].click();", download_btn)
                time.sleep(2)

                bib_saved = False
                try:
                    download_now_btn = WebDriverWait(modal, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.download__btn"))
                    )
                    data_href = download_now_btn.get_attribute("href")
                    if data_href and data_href.startswith("data:"):
                        bib_content = urllib.parse.unquote(data_href.split(",", 1)[1])
                        bib_file = os.path.join(output_dir, f"ACM_{query.replace(' ','_')}_page{page}.bib")
                        with open(bib_file, "w", encoding="utf-8") as f:
                            f.write(bib_content)
                        print(f"[ACM] BibTeX guardado: {bib_file}")
                        bib_saved = True
                except:
                    print("[ACM] Error en proceso de descarga BibTeX, se continúa")

                # ⚠️ Guardar log si no se pudo obtener BibTeX
                if not bib_saved:
                    log_file = os.path.join(output_dir, f"ACM_{query.replace(' ','_')}_page{page}_ERROR.html")
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write(modal.get_attribute("outerHTML"))
                    print(f"[ACM] Guardado HTML del modal para depuración: {log_file}")

            except:
                print("[ACM] No se pudo procesar modal de exportación, se continúa...")

            try:
                results = driver.find_elements(By.CSS_SELECTOR, "h5.issue-item__title a")
                if results:
                    csv_file = os.path.join(output_dir, f"{query.replace(' ','_')}_page{page}.csv")
                    with open(csv_file, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Title", "Link"])
                        for r in results:
                            writer.writerow([r.text, r.get_attribute("href")])
                    print(f"[ACM] CSV guardado: {csv_file}")
            except:
                print("[ACM] No se pudieron extraer títulos, se continúa...")

    finally:
        driver.quit()
        print("[ACM] Proceso finalizado. Revisa la carpeta para BibTeX, CSV y logs de error.")


if __name__ == "__main__":
    import os
    
    # Configuración con rutas relativas multiplataforma
    output_dir = PROJECT_ROOT / "data" / "raw" / "acm"
    chrome_profile = PROJECT_ROOT / "chrome_profile_copy"
    
    # Determinar si ejecutar en headless basado en variable de entorno
    # En despliegue: HEADLESS=true, en desarrollo local: HEADLESS=false o no definida
    headless_mode = os.environ.get('HEADLESS', 'true').lower() == 'true'
    
    fetch_acm_articles(
        query="generative artificial intelligence",
        headless=headless_mode,  # Modo headless por defecto para despliegue
        user_data_dir=str(chrome_profile) if chrome_profile.exists() else None,
        profile_dir="Default",
        output_dir=str(output_dir),
        page_size=50,
        max_pages=5  # ⚡ Limitado a 5 páginas para evitar timeout en despliegue
    )
