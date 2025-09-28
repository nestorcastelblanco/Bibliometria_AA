import os
import time
import csv
import re
import urllib.parse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_total_pages(driver, page_size):
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
                       output_dir="data/raw/acm", page_size=50, max_pages=0):
    """
    Automatiza la descarga de artículos de ACM.
    - Guarda BibTeX y CSV por página.
    - max_pages=0 descarga todas las páginas detectadas.
    """
    print(f"[ACM] Iniciando búsqueda: {query}")
    os.makedirs(output_dir, exist_ok=True)

    options = uc.ChromeOptions()
    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument(f"--profile-directory={profile_dir}")
    if headless:
        options.add_argument("--headless=new")

    driver = uc.Chrome(options=options)
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
    fetch_acm_articles(
        query="generative artificial intelligence",
        headless=False,
        user_data_dir=r"C:\Bibliometria\chrome_profile_copy",
        profile_dir="Default",
        output_dir=r"C:\Bibliometria\data\raw\acm",
        page_size=50,
        max_pages=250 # ⚡ 0 = todas las páginas, >0 = limitar
    )
