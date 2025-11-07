import os
from pathlib import Path
import re
import time  # <-- importamos time

# -------------------------------
# Normalizar campos
# -------------------------------

# Ruta relativa multiplataforma
PROJECT_ROOT = Path(__file__).resolve().parents[3]
def normalize_field(entry, field):
    return entry.get(field, "").strip().lower()


def sort_key(entry):
    year_str = entry.get("year", "").strip()
    try:
        year = int(year_str)
    except ValueError:
        year = 9999
    title = normalize_field(entry, "title")
    return (year, title)

# -------------------------------
# Gnome Sort
# -------------------------------
def gnome_sort(data, key_func):
    arr = data[:]
    index = 0
    n = len(arr)

    while index < n:
        if index == 0 or key_func(arr[index]) >= key_func(arr[index - 1]):
            index += 1
        else:
            arr[index], arr[index - 1] = arr[index - 1], arr[index]
            index -= 1
    return arr

# -------------------------------
# Parsear archivo .bib
# -------------------------------
def parse_bib_file(filepath):
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    raw_entries = re.split(r"@\w+\s*{", content)[1:]
    for raw in raw_entries:
        fields = {}
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
            f.write(f"@article{{{e.get('id','noid')},\n")
            for k, v in e.items():
                if k != "id":
                    f.write(f"  {k} = {{{v}}},\n")
            f.write("}\n\n")

# -------------------------------
# Programa principal
# -------------------------------
if __name__ == "__main__":
    input_file = PROJECT_ROOT / "data" / "processed" / "productos_unificados.bib"
    output_dir = PROJECT_ROOT / "data" / "processed" / "ordenamiento"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "ordenado_gnome.bib")

    if not os.path.exists(input_file):
        print(f"[ERROR] No se encontró el archivo {input_file}")
        exit(1)

    print(f"[INFO] Leyendo {input_file}...")
    entries = parse_bib_file(input_file)
    print(f"[INFO] {len(entries)} entradas encontradas")

    print("[INFO] Ordenando con Gnome Sort por (año, título)...")
    start_time = time.time()  # <-- inicio de medición
    sorted_entries = gnome_sort(entries, sort_key)
    end_time = time.time()    # <-- fin de medición
    print(f"[INFO] Tiempo de ejecución: {end_time - start_time:.6f} segundos")  # <-- mostrar tiempo

    print(f"[INFO] Guardando en {output_file}...")
    save_bib(sorted_entries, output_file)

    print("[OK] Proceso completado ✅")
