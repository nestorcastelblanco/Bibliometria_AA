import os
import re
import time  # <-- importar time

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
# Bitonic Sort
# -------------------------------
def comp_and_swap(arr, i, j, dire, key_func):
    if (dire == 1 and key_func(arr[i]) > key_func(arr[j])) or (dire == 0 and key_func(arr[i]) < key_func(arr[j])):
        arr[i], arr[j] = arr[j], arr[i]


def bitonic_merge(arr, low, cnt, dire, key_func):
    if cnt > 1:
        k = cnt // 2
        for i in range(low, low + k):
            comp_and_swap(arr, i, i + k, dire, key_func)
        bitonic_merge(arr, low, k, dire, key_func)
        bitonic_merge(arr, low + k, k, dire, key_func)


def bitonic_sort_rec(arr, low, cnt, dire, key_func):
    if cnt > 1:
        k = cnt // 2
        bitonic_sort_rec(arr, low, k, 1, key_func)
        bitonic_sort_rec(arr, low + k, k, 0, key_func)
        bitonic_merge(arr, low, cnt, dire, key_func)


def bitonic_sort(data, key_func):
    arr = data[:]
    n = len(arr)
    # Para bitonic sort, la longitud debe ser potencia de 2 → rellenamos con dummies
    m = 1
    while m < n:
        m *= 2
    while len(arr) < m:
        arr.append({"id": "zzzz_dummy", "year": "9999", "title": "zzzz_dummy"})

    bitonic_sort_rec(arr, 0, len(arr), 1, key_func)

    # Quitamos dummies
    arr = [x for x in arr if x.get("id") != "zzzz_dummy"]
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

    output_file = os.path.join(output_dir, "ordenado_bitonic.bib")

    if not os.path.exists(input_file):
        print(f"[ERROR] No se encontró el archivo {input_file}")
        exit(1)

    print(f"[INFO] Leyendo {input_file}...")
    entries = parse_bib_file(input_file)
    print(f"[INFO] {len(entries)} entradas encontradas")

    print("[INFO] Ordenando con Bitonic Sort por (año, título)...")
    start_time = time.time()  # <-- inicio del conteo
    sorted_entries = bitonic_sort(entries, sort_key)
    end_time = time.time()    # <-- fin del conteo
    elapsed = end_time - start_time
    print(f"[INFO] Tiempo de ejecución: {elapsed:.6f} segundos")  # <-- mostrar tiempo

    print(f"[INFO] Guardando en {output_file}...")
    save_bib(sorted_entries, output_file)

    print("[OK] Proceso completado ✅")
