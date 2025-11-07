import os
import re
import unicodedata
import time
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt
from pathlib import Path

# Configurar rutas multiplataforma
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Ruta relativa multiplataforma
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# -------------------------------
# Normalizar campos
# -------------------------------
def normalize_field(entry, field):
    val = entry.get(field, "").strip().lower()
    return unicodedata.normalize("NFKD", val).encode("ascii", "ignore").decode("ascii")


def sort_key(entry):
    year_str = entry.get("year", "").strip()
    try:
        year = int(year_str)
    except ValueError:
        year = 9999
    title = normalize_field(entry, "title")
    return (year, title)

# -------------------------------
# Parsear archivo .bib
# -------------------------------
def parse_bib_file(filepath):
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    raw_entries = re.split(r"@(\w+)\s*{", content)[1:]
    for i in range(0, len(raw_entries), 2):
        type_entry = raw_entries[i].strip().lower()
        raw = raw_entries[i+1]

        fields = {"type": type_entry}
        match_key = re.match(r"([^,]+),", raw.strip())
        if match_key:
            fields["id"] = match_key.group(1).strip()

        for match in re.finditer(r"(\w+)\s*=\s*[{\"](.*?)[}\"]\s*,", raw, re.DOTALL):
            field, value = match.groups()
            fields[field.lower()] = value.replace("\n", " ").strip()

        entries.append(fields)

    return entries

# -------------------------------
# Guardar archivo .bib
# -------------------------------
def save_bib(entries, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(f"@{e.get('type','article')}{{{e.get('id','noid')},\n")
            for k, v in e.items():
                if k not in ["id", "type"]:
                    f.write(f"  {k} = {{{v}}},\n")
            f.write("}\n\n")

# -------------------------------
# Contar autores
# -------------------------------
def top_authors(entries, top_n=15):
    all_authors = []
    for e in entries:
        authors_field = e.get("author", "")
        authors = [normalize_field({"author": a}, "author") for a in re.split(r"\s+and\s+", authors_field)]
        # Filtrar autores vacíos
        authors = [a for a in authors if a]
        all_authors.extend(authors)
    counter = Counter(all_authors)
    most_common = counter.most_common(top_n)
    # Orden ascendente por cantidad de apariciones
    most_common_sorted = sorted(most_common, key=lambda x: x[1])
    return most_common_sorted

# -------------------------------
# Graficar top autores
# -------------------------------
def plot_top_authors(top_authors_list):
    authors, counts = zip(*top_authors_list)
    plt.figure(figsize=(12, 6))
    plt.barh(authors, counts, color='skyblue')
    plt.xlabel("Número de apariciones")
    plt.ylabel("Autores")
    plt.title("Top 15 autores con más apariciones en productos académicos")
    plt.tight_layout()
    plt.show()

# -------------------------------
# Programa principal
# -------------------------------
if __name__ == "__main__":
    input_file = PROJECT_ROOT / "data" / "processed" / "productos_unificados.bib"
    output_dir = PROJECT_ROOT / "data" / "processed" / "ordenamiento"
<<<<<<< Updated upstream
    output_dir.mkdir(parents=True, exist_ok=True)
=======
    os.makedirs(output_dir, exist_ok=True)
>>>>>>> Stashed changes

    output_file = output_dir / "ordenado_timsort.bib"

    if not input_file.exists():
        print(f"[ERROR] No se encontró el archivo {input_file}")
        exit(1)

    print(f"[INFO] Leyendo {input_file}...")
    entries = parse_bib_file(str(input_file))
    print(f"[INFO] {len(entries)} entradas encontradas")

    print("[INFO] Ordenando con Timsort por (año, título)...")
    start_time = time.time()
    sorted_entries = sorted(entries, key=sort_key)
    end_time = time.time()
    print(f"[INFO] Tiempo de ordenamiento: {end_time - start_time:.6f} seg")

    print(f"[INFO] Guardando en {output_file}...")
    save_bib(sorted_entries, str(output_file))
    print("[OK] Proceso completado ✅")

    # -------------------------------
    # Mostrar top 15 autores
    # -------------------------------
    top15 = top_authors(entries, top_n=15)
    print("\nTop 15 autores con más apariciones (orden ascendente por cantidad):")
    for author, count in top15:
        print(f"{author}: {count}")

    # -------------------------------
    # Graficar top 15 autores
    # -------------------------------
    plot_top_authors(top15)
