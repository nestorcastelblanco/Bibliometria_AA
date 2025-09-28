#!/usr/bin/env python3
import os
import re
import time
import bibtexparser
from collections import defaultdict

RAW_DIR = r"C:\Bibliometria\data\raw"
PROCESSED_DIR = r"C:\Bibliometria\data\processed"

# ---------- utilidades ----------

def normalize_title(title: str) -> str:
    if not title:
        return ""
    s = title
    s = re.sub(r"^\s*[{\"]|[}\"]\s*$", "", s)            # quitar llaves/comillas externas
    s = re.sub(r'\\[A-Za-z]+\*?\{([^}]*)\}', r'\1', s)  # \cmd{...} -> ...
    s = re.sub(r'\\[A-Za-z]+\*?', '', s)                # \cmd -> ''
    s = re.sub(r"[^0-9A-Za-zÀ-ÖØ-öø-ÿ\s]", " ", s)      # quitar símbolos manteniendo letras
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def extract_title_from_raw(raw: str) -> str:
    m = re.search(r"title\s*=\s*[{\"](.+?)[}\"]", raw, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""

def entry_to_raw(entry: dict) -> str:
    """Si entry tiene _raw lo devuelve; sino intenta crear un bloque .bib via bibtexparser."""
    if entry.get("_raw"):
        return entry["_raw"].strip() + "\n"
    # fallback: generar una entrada .bib mínima
    db = bibtexparser.bibdatabase.BibDatabase()
    # evito campos internos
    e = {k: v for k, v in entry.items() if not k.startswith("_")}
    db.entries = [e]
    return bibtexparser.dumps(db).strip() + "\n"

# ---------- carga y parseo robusto ----------

def find_bib_files(raw_dir=RAW_DIR):
    files = []
    for root, _, filenames in os.walk(raw_dir):
        for fn in filenames:
            if fn.lower().endswith(".bib"):
                files.append(os.path.join(root, fn))
    files.sort()
    return files

def parse_bib_file(path):
    """Intenta parsear todo el archivo; si falla, divide en bloques '@' y parsea cada bloque."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    entries = []
    try:
        db = bibtexparser.loads(text)
        if db.entries:
            # attach raw: try to map raw blocks by ID
            raw_blocks = [blk if blk.startswith("@") else "@" + blk for blk in re.split(r'\n(?=@)', text) if blk.strip()]
            raw_map = {}
            for blk in raw_blocks:
                m = re.match(r'@\s*(\w+)\s*{\s*([^,]+)\s*,', blk, re.DOTALL)
                if m:
                    raw_map[m.group(2).strip()] = blk
            for e in db.entries:
                ee = dict(e)
                key = ee.get("ID") or ee.get("id") or ee.get("key")
                if key and key in raw_map:
                    ee["_raw"] = raw_map[key]
                else:
                    # fallback: try match title in blocks
                    title = ee.get("title", "")
                    found = None
                    if title:
                        for blk in raw_blocks:
                            if title.split()[0].lower() in blk.lower():
                                found = blk; break
                    ee["_raw"] = found
                entries.append(ee)
            return entries, None
    except Exception as e:
        parse_error = e

    # fallback por bloques: extraer bloques que empiezan con @...{ ... } (no perfecto pero funciona)
    blocks = re.findall(r'@[^@{]+\{[^@]*?(?=\n@|$)', text, re.DOTALL)
    if not blocks:
        # último recurso: separar por línea que empiece con @
        blocks = re.split(r'\n(?=@)', text)
    for blk in blocks:
        blk = blk.strip()
        if not blk:
            continue
        blk2 = blk if blk.startswith("@") else "@" + blk
        # intentar parsear el bloque entero con bibtexparser
        try:
            dbb = bibtexparser.loads(blk2)
            if dbb.entries:
                ee = dict(dbb.entries[0])
                ee["_raw"] = blk2
                entries.append(ee)
                continue
        except:
            pass
        # si no se pudo parsear, crear una entrada mínima con título extraído del raw
        t = extract_title_from_raw(blk2)
        ee = {"title": t, "_raw": blk2}
        entries.append(ee)

    return entries, parse_error if 'parse_error' in locals() else None

# ---------- unificación con diagnóstico ----------

def unify_all(raw_dir=RAW_DIR, processed_dir=PROCESSED_DIR,
              out_unique="productos_unificados.bib", out_duplicates="duplicados.bib"):
    os.makedirs(processed_dir, exist_ok=True)
    files = find_bib_files(raw_dir)
    if not files:
        print("[WARN] No se encontraron archivos .bib en", raw_dir)
        return

    print(f"[INFO] Archivos .bib encontrados: {len(files)}")
    per_folder = {}
    per_file_entries = {}
    all_entries = []
    parse_errors = {}

    for p in files:
        folder = os.path.basename(os.path.dirname(p))
        per_folder[folder] = per_folder.get(folder, 0) + 1
        entries, err = parse_bib_file(p)
        per_file_entries[p] = len(entries)
        all_entries.extend([dict(e, _source=os.path.basename(p)) for e in entries])
        if err:
            parse_errors[p] = str(err)

    # imprimir resumen archivos / carpetas / entradas
    print("Resumen por carpeta (nº archivos):")
    for k, v in per_folder.items():
        print(f"  - {k}: {v} archivos")
    print("\nEntradas extraídas por archivo (muestra parcial):")
    shown = 0
    for p, cnt in per_file_entries.items():
        print(f"  - {os.path.relpath(p, raw_dir)} : {cnt} entradas")
        shown += 1
        if shown >= 10: break
    total_entries = len(all_entries)
    print(f"\n[INFO] Total de entradas extraídas: {total_entries}")
    if parse_errors:
        print("\n[WARN] Errores de parseo en algunos archivos (se incluyeron por fallback):")
        for p, err in parse_errors.items():
            print(f"  - {os.path.relpath(p, raw_dir)} : {err}")

    # deduplicación por título normalizado (fallback DOI/ID)
    seen = {}
    duplicates = []
    for e in all_entries:
        title = e.get("title", "") or ""
        norm = normalize_title(title)
        if not norm:  # fallback a DOI o ID o combinación source+index
            norm = normalize_title(e.get("doi", "") or e.get("ID","") or (e.get("_source","") + "_" + str(hash(entry_to_raw(e)))))

        if norm in seen:
            duplicates.append(e)
        else:
            seen[norm] = e

    # guardar unificado y duplicados preservando raw cuando haya
    unique_path = os.path.join(processed_dir, out_unique)
    with open(unique_path, "w", encoding="utf-8") as out:
        for e in seen.values():
            out.write(f"% Fuente: {e.get('_source','unknown')}\n")
            out.write(entry_to_raw(e))
            out.write("\n")

    dup_path = os.path.join(processed_dir, out_duplicates)
    with open(dup_path, "w", encoding="utf-8") as out:
        for e in duplicates:
            out.write(f"% Fuente (duplicado): {e.get('_source','unknown')}\n")
            out.write(entry_to_raw(e))
            out.write("\n")

    print(f"\n[OK] Archivo unificado guardado en: {unique_path} (únicos: {len(seen)})")
    print(f"[OK] Archivo de duplicados guardado en: {dup_path} (duplicados: {len(duplicates)})")
    return {
        "files_found": files,
        "per_folder": per_folder,
        "per_file_entries": per_file_entries,
        "total_entries": total_entries,
        "unique_count": len(seen),
        "duplicates_count": len(duplicates),
        "unique_path": unique_path,
        "dup_path": dup_path
    }

# ---------- ejecución ----------

if __name__ == "__main__":
    start = time.time()
    summary = unify_all()
    print("\nTiempo total:", time.time() - start, "seg")
