"""
Scraper automatizado para descarga de artículos desde SAGE Journals.

Implementa web scraping con Selenium y undetected-chromedriver para:
- Realizar búsquedas en SAGE Journals
- Navegar automáticamente por todas las páginas disponibles
- Seleccionar artículos de cada página
- Exportar referencias en formato BibTeX
- Guardar metadata en CSV

Características:
- Detección automática de paginación
- Soporte para sesiones autenticadas (perfil de Chrome)
- Modo headless para ejecución en background
- Descarga directa de BibTeX desde data:// URI
- Navegación secuencial hasta última página
- Logging detallado del progreso

Parte del Requerimiento 1: Scraping de bibliografía académica.
"""
import os
import time
import csv
import urllib.parse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_sage_bibtex(query, output_dir="data/raw/acm", headless=False,
                       user_data_dir=None, profile_dir="Default"):
    """
    Automatiza descarga masiva de artículos desde SAGE Journals.
    
    A diferencia de ACM, SAGE no muestra total de páginas por adelantado,
    por lo que este scraper navega página por página hasta encontrar el final.
    
    Pipeline completo:
    1. Configura Chrome con perfil (para autenticación)
    2. Realiza búsqueda en SAGE Journals
    3. Itera sobre páginas hasta que no haya botón "next"
    4. Por cada página:
       a. Selecciona todos los artículos
       b. Abre modal de exportación
       c. Selecciona formato BibTeX
       d. Descarga BibTeX desde data:// URI
       e. Guarda CSV con títulos y enlaces
       f. Navega a siguiente página
    5. Cierra navegador y reporta resultados
    
    Args:
        query (str): Término de búsqueda (ej: "machine learning")
        output_dir (str, optional): Directorio donde guardar archivos.
                                   Default: "data/raw/acm"
        headless (bool, optional): Ejecutar sin interfaz gráfica. Default: False
        user_data_dir (str, optional): Directorio de perfil de Chrome.
                                      Útil si requiere autenticación. Default: None
        profile_dir (str, optional): Nombre del perfil dentro de user_data_dir.
                                    Default: "Default"
    
    Archivos generados por página:
        - SAGE_{query}_page{N}.bib: Referencias BibTeX
        - SAGE_{query}_page{N}.csv: Tabla con títulos y enlaces
    
    Process detallado:
        1. Crea directorio de salida si no existe
        2. Configura ChromeOptions con perfil y headless
        3. Inicializa undetected_chromedriver
        4. Construye URL de búsqueda SAGE
        5. Navega y espera carga inicial
        6. Inicia contador de páginas en 1
        7. Loop infinito hasta que no haya "next":
           - Selecciona todos con input#action-bar-select-all
           - Click en botón export-citation
           - Espera modal #exportCitation
           - Selecciona BibTeX en dropdown #citation-format
           - Extrae href de a.download__btn
           - Decodifica data:// URI y guarda .bib
           - Extrae títulos de h5.issue-item__title
           - Guarda CSV
           - Busca enlace a[aria-label='next']
           - Si existe: navega y continúa
           - Si no existe: break y finaliza
        8. Cierra driver en finally
    
    Diferencias vs ACM:
        - No conoce total de páginas por adelantado
        - Usa aria-label='next' para navegación
        - Modal ID es #exportCitation (vs ACM)
        - Selector de "todos" es input#action-bar-select-all
    
    Manejo de errores:
        - Intenta cada paso pero continúa si falla
        - Print de mensajes informativos
        - No detiene proceso ante errores individuales
        - Always ejecuta driver.quit() en finally
    
    Example:
        >>> fetch_sage_bibtex(
        ...     query="deep learning",
        ...     output_dir="./downloads/sage",
        ...     headless=True
        ... )
        [SAGE] Procesando página 1...
        [SAGE] BibTeX guardado: ./downloads/sage/SAGE_deep_learning_page1.bib
        [SAGE] CSV guardado: ./downloads/sage/SAGE_deep_learning_page1.csv
        [SAGE] Procesando página 2...
        ...
        [SAGE] No hay más páginas.
        [SAGE] Proceso finalizado.
    
    Requisitos:
        - undetected_chromedriver instalado
        - Chrome/Chromium instalado
        - Conexión a internet
        - Opcionalmente: sesión SAGE autenticada
    
    Notas:
        - Procesa TODAS las páginas automáticamente (no hay límite)
        - Puede ser muy largo para queries amplios
        - user_data_dir útil para mantener sesión
        - Incluye sleeps para evitar rate limiting
        - Usa JavaScript para clicks (evita interceptación)
        - SAGE típicamente tiene menos resultados que ACM
    """
    os.makedirs(output_dir, exist_ok=True)
    options = uc.ChromeOptions()
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument(f"--profile-directory={profile_dir}")
    if headless:
        options.add_argument("--headless=new")
    
    driver = uc.Chrome(options=options)

    try:
        search_url = f"https://journals.sagepub.com/action/doSearch?AllField={query.replace(' ','+')}"
        driver.get(search_url)
        time.sleep(2)

        current_page = 1
        while True:
            print(f"[SAGE] Procesando página {current_page}...")

            # 1️⃣ Seleccionar todos los artículos
            try:
                select_all = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input#action-bar-select-all"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", select_all)
                time.sleep(1)
            except:
                print("[SAGE] No se encontró 'Seleccionar todo'.")

            # 2️⃣ Abrir modal de exportación
            try:
                export_btn = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.article-actionbar__btn.export-citation"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", export_btn)
                time.sleep(2)
            except:
                print("[SAGE] No se encontró botón de exportación.")

            # 3️⃣ Esperar modal
            try:
                modal = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.ID, "exportCitation"))
                )
                time.sleep(1)
            except:
                print("[SAGE] Modal no apareció.")
                modal = None

            # 4️⃣ Seleccionar BibTeX y descargar
            if modal:
                try:
                    select = modal.find_element(By.ID, "citation-format")
                    for option in select.find_elements(By.TAG_NAME, "option"):
                        if option.get_attribute("value").lower() == "bibtex":
                            option.click()
                            break
                    time.sleep(1)

                    download_link = WebDriverWait(modal, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.download__btn"))
                    )
                    href = download_link.get_attribute("href")
                    if href.startswith("data:"):
                        bib_content = urllib.parse.unquote(href.split(",")[1])
                        bib_file = os.path.join(output_dir, f"SAGE_{query.replace(' ','_')}_page{current_page}.bib")
                        with open(bib_file, "w", encoding="utf-8") as f:
                            f.write(bib_content)
                        print(f"[SAGE] BibTeX guardado: {bib_file}")
                except:
                    print("[SAGE] Error al descargar BibTeX.")

            # 5️⃣ Guardar CSV con títulos y enlaces
            try:
                results = driver.find_elements(By.CSS_SELECTOR, "h5.issue-item__title a")
                if results:
                    csv_file = os.path.join(output_dir, f"SAGE_{query.replace(' ','_')}_page{current_page}.csv")
                    with open(csv_file, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Title", "Link"])
                        for r in results:
                            writer.writerow([r.text, r.get_attribute("href")])
                    print(f"[SAGE] CSV guardado: {csv_file}")
            except:
                print("[SAGE] Error al guardar CSV.")

            # 6️⃣ Ir a siguiente página si existe
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "a[aria-label='next']")
                next_href = next_btn.get_attribute("href")
                if next_href:
                    driver.get(next_href)
                    time.sleep(3)
                    current_page += 1
                else:
                    print("[SAGE] No hay más páginas.")
                    break
            except:
                print("[SAGE] No hay más páginas.")
                break

    finally:
        driver.quit()
        print("[SAGE] Proceso finalizado. Revisa la carpeta para BibTeX y CSV.")

# ===== EJECUTAR =====
# ===== EJECUTAR =====
if __name__ == "__main__":
    fetch_sage_bibtex(
        query="Generative Artificial Intelligence",
        output_dir=r"C:\Bibliometria\data\raw\sage",  # ✅ carpeta única para ACM y SAGE
        headless=False,
        user_data_dir=r"C:\Bibliometria\chrome_profile_copy",
        profile_dir="Default"
    )

