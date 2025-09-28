import os
import re
import time  # <-- Importamos time

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
# Radix Sort (para enteros)
# -------------------------------
def counting_sort(arr, exp, key_func):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = (key_func(arr[i])[0] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    i = n - 1
    while i >= 0:
        index = (key_func(arr[i])[0] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1
        i -= 1

    for i in range(n):
        arr[i] = output[i]


def radix_sort(arr, key_func):
    try:
        max_year = max(int(e.get("year", "0") or 0) for e in arr)
    except ValueError:
        max_year = 0

    exp = 1
    while max_year // exp > 0:
        counting_sort(arr, exp, key_func)
        exp *= 10

    arr.sort(key=lambda e: (key_func(e)[0], key_func(e)[1]))
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

    output_file = os.path.join(output_dir, "ordenado_radix.bib")

    if not os.path.exists(input_file):
        print(f"[ERROR] No se encontró el archivo {input_file}")
        exit(1)

    print(f"[INFO] Leyendo {input_file}...")
    entries = parse_bib_file(input_file)
    print(f"[INFO] {len(entries)} entradas encontradas")

    print("[INFO] Ordenando con Radix Sort por (año, título)...")
    start_time = time.time()  # <-- inicio tiempo
    sorted_entries = radix_sort(entries, sort_key)
    end_time = time.time()    # <-- fin tiempo
    print(f"[INFO] Tiempo de ejecución: {end_time - start_time:.6f} segundos")

    print(f"[INFO] Guardando en {output_file}...")
    save_bib(sorted_entries, output_file)

    print("[OK] Proceso completado ✅")
