import os
import bibtexparser
import unicodedata
import time

# ================== RUTAS ================== #
INPUT_FILE = r"C:\Bibliometria\data\processed\productos_unificados.bib"
OUTPUT_DIR = r"C:\Bibliometria\data\processed\ordenamiento"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ordenado_selection.bib")

# ================== FUNCIONES AUXILIARES ================== #
def normalize_field(entry, key):
    """Normaliza el campo a minúsculas y sin tildes."""
    val = entry.get(key, "").strip().lower()
    return unicodedata.normalize("NFKD", val).encode("ascii", "ignore").decode("ascii")

def get_sort_key(entry):
    """Clave de ordenamiento: primero año (asc), luego título (asc)."""
    year = entry.get("year", "").strip()
    try:
        year = int(year)
    except ValueError:
        year = 0  # si no hay año válido
    title = normalize_field(entry, "title")
    return (year, title)

def save_bib(entries, filename):
    """Guarda una lista de entradas en formato .bib."""
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = entries
    with open(filename, "w", encoding="utf-8") as f:
        f.write(bibtexparser.dumps(db))

# ================== SELECTION SORT ================== #
def selection_sort(data):
    arr = data[:]
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if get_sort_key(arr[j]) < get_sort_key(arr[min_idx]):
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

# ================== MAIN ================== #
if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"No se encontró {INPUT_FILE}")

    print("[INFO] Cargando archivo productos_unificados.bib...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        bib_database = bibtexparser.load(f)
        entries = bib_database.entries
    print(f"[INFO] Total entradas cargadas: {len(entries)}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("[INFO] Ordenando con Selection Sort (año, título)...")
    start = time.time()
    sorted_entries = selection_sort(entries)
    end = time.time()

    save_bib(sorted_entries, OUTPUT_FILE)
    print(f"[OK] Guardado en {OUTPUT_FILE} ({end - start:.6f} seg)")
