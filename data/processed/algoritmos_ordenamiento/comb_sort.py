import os
import re
import time  # <-- importamos time

# -------------------------------
# Normalizar campos
# -------------------------------
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
# Comb Sort
# -------------------------------
def comb_sort(data, key_func):
    arr = data[:]
    gap = len(arr)
    shrink = 1.3
    sorted_flag = False

    while not sorted_flag:
        gap = int(gap / shrink)
        if gap < 1:
            gap = 1
        sorted_flag = True

        for i in range(len(arr) - gap):
            if key_func(arr[i]) > key_func(arr[i + gap]):
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                sorted_flag = False

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
    input_file = r"C:\Bibliometria\data\processed\productos_unificados.bib"
    output_dir = r"C:\Bibliometria\data\processed\ordenamiento"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "ordenado_comb.bib")

    if not os.path.exists(input_file):
        print(f"[ERROR] No se encontró el archivo {input_file}")
        exit(1)

    print(f"[INFO] Leyendo {input_file}...")
    entries = parse_bib_file(input_file)
    print(f"[INFO] {len(entries)} entradas encontradas")

    print("[INFO] Ordenando con Comb Sort por (año, título)...")
    start_time = time.time()  # <-- inicio de medición
    sorted_entries = comb_sort(entries, sort_key)
    end_time = time.time()    # <-- fin de medición
    print(f"[INFO] Tiempo de ejecución: {end_time - start_time:.6f} segundos")  # <-- mostrar tiempo

    print(f"[INFO] Guardando en {output_file}...")
    save_bib(sorted_entries, output_file)

    print("[OK] Proceso completado ✅")
