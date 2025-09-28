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
# Ordenamiento Binary Insertion
# -------------------------------
def binary_insertion_sort(data, key_func):
    arr = data[:]

    def binary_search(sub_arr, val, start, end):
        if start == end:
            return start if key_func(val) < key_func(sub_arr[start]) else start + 1
        if start > end:
            return start

        mid = (start + end) // 2
        if key_func(val) < key_func(sub_arr[mid]):
            return binary_search(sub_arr, val, start, mid - 1)
        elif key_func(val) > key_func(sub_arr[mid]):
            return binary_search(sub_arr, val, mid + 1, end)
        else:
            return mid + 1

    for i in range(1, len(arr)):
        val = arr[i]
        j = binary_search(arr, val, 0, i - 1)
        arr = arr[:j] + [val] + arr[j:i] + arr[i + 1:]

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

    output_file = os.path.join(output_dir, "ordenado_binary.bib")

    if not os.path.exists(input_file):
        print(f"[ERROR] No se encontró el archivo {input_file}")
        exit(1)

    print(f"[INFO] Leyendo {input_file}...")
    entries = parse_bib_file(input_file)
    print(f"[INFO] {len(entries)} entradas encontradas")

    print("[INFO] Ordenando con Binary Insertion Sort por (año, título)...")
    start_time = time.time()  # <-- inicio del conteo
    sorted_entries = binary_insertion_sort(entries, sort_key)
    end_time = time.time()    # <-- fin del conteo

    elapsed = end_time - start_time
    print(f"[INFO] Tiempo de ejecución: {elapsed:.6f} segundos")  # <-- mostrar tiempo

    print(f"[INFO] Guardando en {output_file}...")
    save_bib(sorted_entries, output_file)

    print("[OK] Proceso completado ✅")
