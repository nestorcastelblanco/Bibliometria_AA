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
# Bucket Sort
# -------------------------------
def insertion_sort(arr, key_func):
    for i in range(1, len(arr)):
        up = arr[i]
        j = i - 1
        while j >= 0 and key_func(arr[j]) > key_func(up):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = up
    return arr


def bucket_sort(data, key_func):
    if not data:
        return []

    # extraemos claves (solo por año)
    keys = [key_func(e)[0] for e in data]
    min_key, max_key = min(keys), max(keys)
    bucket_count = max(1, len(data) // 5)  # número de cubetas aproximado
    bucket_range = (max_key - min_key + 1) / bucket_count

    # inicializamos cubetas
    buckets = [[] for _ in range(bucket_count)]

    # distribuimos
    for e in data:
        idx = int((key_func(e)[0] - min_key) // bucket_range)
        if idx >= bucket_count:
            idx = bucket_count - 1
        buckets[idx].append(e)

    # ordenamos dentro de cada bucket
    sorted_data = []
    for b in buckets:
        sorted_data.extend(insertion_sort(b, key_func))

    # si hay empate por año, lo resolvemos por título
    sorted_data = sorted(sorted_data, key=key_func)
    return sorted_data

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

    output_file = os.path.join(output_dir, "ordenado_bucket.bib")

    if not os.path.exists(input_file):
        print(f"[ERROR] No se encontró el archivo {input_file}")
        exit(1)

    print(f"[INFO] Leyendo {input_file}...")
    entries = parse_bib_file(input_file)
    print(f"[INFO] {len(entries)} entradas encontradas")

    print("[INFO] Ordenando con Bucket Sort por (año, título)...")
    start_time = time.time()  # <-- inicio
    sorted_entries = bucket_sort(entries, sort_key)
    end_time = time.time()    # <-- fin
    elapsed = end_time - start_time
    print(f"[INFO] Tiempo de ejecución: {elapsed:.6f} segundos")  # <-- mostrar tiempo

    print(f"[INFO] Guardando en {output_file}...")
    save_bib(sorted_entries, output_file)

    print("[OK] Proceso completado ✅")
