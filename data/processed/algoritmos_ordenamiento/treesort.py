import os
from pathlib import Path
import re
import unicodedata
import time

# -------------------------------
# Normalizar campos
# -------------------------------

# Ruta relativa multiplataforma
PROJECT_ROOT = Path(__file__).resolve().parents[3]
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
# TreeSort
# -------------------------------
class TreeNode:
    def __init__(self, entry):
        self.entry = entry
        self.left = None
        self.right = None

def insert(node, entry):
    if node is None:
        return TreeNode(entry)
    if sort_key(entry) < sort_key(node.entry):
        node.left = insert(node.left, entry)
    else:
        node.right = insert(node.right, entry)
    return node

def inorder_traversal(node, result):
    if node is not None:
        inorder_traversal(node.left, result)
        result.append(node.entry)
        inorder_traversal(node.right, result)

def treesort(entries):
    root = None
    for entry in entries:
        root = insert(root, entry)
    sorted_entries = []
    inorder_traversal(root, sorted_entries)
    return sorted_entries

# -------------------------------
# Programa principal
# -------------------------------
if __name__ == "__main__":
    input_file = PROJECT_ROOT / "data" / "processed" / "productos_unificados.bib"
    output_dir = PROJECT_ROOT / "data" / "processed" / "ordenamiento"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "ordenado_treesort.bib")

    if not os.path.exists(input_file):
        print(f"[ERROR] No se encontró el archivo {input_file}")
        exit(1)

    print(f"[INFO] Leyendo {input_file}...")
    entries = parse_bib_file(input_file)
    print(f"[INFO] {len(entries)} entradas encontradas")

    print("[INFO] Ordenando con TreeSort por (año, título)...")
    start_time = time.time()
    sorted_entries = treesort(entries)
    end_time = time.time()
    print(f"[INFO] Tiempo de ordenamiento: {end_time - start_time:.6f} seg")

    print(f"[INFO] Guardando en {output_file}...")
    save_bib(sorted_entries, output_file)

    print("[OK] Proceso completado ✅")
