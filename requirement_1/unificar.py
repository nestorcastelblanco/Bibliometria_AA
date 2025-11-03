#!/usr/bin/env python3
"""
Script de unificación y deduplicación de archivos BibTeX bibliográficos.

Funcionalidades principales:
- Búsqueda recursiva de archivos .bib en directorios
- Parseo robusto con fallback para archivos malformados
- Normalización de títulos para detección de duplicados
- Preservación de contenido raw original
- Generación de archivos unificados y de duplicados
- Diagnóstico detallado del proceso

Pipeline:
    1. Encuentra todos los .bib en directorio raw
    2. Parsea cada archivo (con estrategia de fallback)
    3. Normaliza títulos para comparación
    4. Detecta y separa duplicados
    5. Genera archivo único y archivo de duplicados
    6. Reporta estadísticas completas

Parte del Requerimiento 1: Scraping y unificación de bibliografía.
"""
import os
import re
import time
import bibtexparser
from collections import defaultdict

RAW_DIR = r"C:\Bibliometria\data\raw"
PROCESSED_DIR = r"C:\Bibliometria\data\processed"



# ---------- utilidades ----------

def normalize_title(title: str) -> str:
    """
    Normaliza título bibliográfico para comparación robusta.
    
    Elimina comandos LaTeX, caracteres especiales, múltiples espacios,
    y convierte a minúsculas para detección de duplicados.
    
    Args:
        title (str): Título original (puede incluir LaTeX)
    
    Returns:
        str: Título normalizado en minúsculas sin símbolos
    
    Process:
        1. Elimina llaves y comillas externas
        2. Elimina comandos LaTeX \\cmd{...} → ...
        3. Elimina comandos LaTeX sin argumentos \\cmd → ''
        4. Elimina símbolos manteniendo letras y números
        5. Normaliza espacios múltiples a uno
        6. Convierte a minúsculas
    
    Example:
        >>> normalize_title("{Machine \\textbf{Learning} Models}")
        'machine learning models'
        >>> normalize_title("AI: The Future")
        'ai the future'
    
    Notas:
        - Soporta caracteres Unicode (acentos, ñ, etc.)
        - Preserva dígitos en el título
        - Útil para detectar duplicados con variaciones de formato
        - Retorna string vacío si title es None o vacío
    """
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
    """
    Extrae título de bloque BibTeX raw usando regex.
    
    Busca el campo title = {...} o title = "..." en el bloque
    BibTeX sin parsear.
    
    Args:
        raw (str): Bloque de texto BibTeX completo
    
    Returns:
        str: Título extraído o string vacío si no se encuentra
    
    Example:
        >>> raw = '@article{key, title = {Machine Learning}, author={Smith}}'
        >>> extract_title_from_raw(raw)
        'Machine Learning'
    
    Notas:
        - Fallback cuando bibtexparser falla
        - Usa regex con DOTALL para títulos multilínea
        - Case-insensitive para flexibilidad
        - Retorna string vacío si no hay match
    """
    m = re.search(r"title\s*=\s*[{\"](.+?)[}\"]", raw, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""

def entry_to_raw(entry: dict) -> str:
    """
    Convierte entrada de diccionario a formato BibTeX raw.
    
    Si la entrada tiene campo '_raw' (bloque original), lo retorna.
    Si no, genera bloque BibTeX mínimo usando bibtexparser.
    
    Args:
        entry (dict): Diccionario con datos de entrada bibliográfica
                     Puede incluir campo '_raw' con bloque original
    
    Returns:
        str: Bloque BibTeX formateado con salto de línea final
    
    Process:
        1. Si existe entry['_raw']: retornar raw + newline
        2. Si no: crear BibDatabase con campos (excepto internos _*)
        3. Usar bibtexparser.dumps() para generar BibTeX
        4. Retornar bloque + newline
    
    Example:
        >>> entry = {'title': 'ML', 'author': 'Smith', '_raw': '@article{...}'}
        >>> entry_to_raw(entry)
        '@article{...}\\n'
    
    Notas:
        - Preserva formato original cuando existe '_raw'
        - Genera fallback válido para entradas sin raw
        - Filtra campos internos que empiezan con '_'
        - Útil para exportar archivo unificado preservando formato
    """
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
    """
    Encuentra recursivamente todos los archivos .bib en directorio.
    
    Args:
        raw_dir (str, optional): Directorio raíz para búsqueda. 
                                Default: RAW_DIR (C:\\Bibliometria\\data\\raw)
    
    Returns:
        List[str]: Lista de rutas absolutas a archivos .bib, ordenada
    
    Process:
        1. Recorre árbol de directorios con os.walk
        2. Filtra archivos con extensión .bib (case-insensitive)
        3. Construye rutas completas con os.path.join
        4. Ordena alfabéticamente
    
    Example:
        >>> files = find_bib_files("C:\\data\\raw")
        >>> files
        ['C:\\data\\raw\\acm\\articles.bib', 'C:\\data\\raw\\sage\\papers.bib']
    
    Notas:
        - Búsqueda recursiva en subdirectorios
        - Case-insensitive para extensión (.bib, .BIB, .Bib)
        - Lista ordenada para procesamiento consistente
        - Útil para encontrar todos los BibTeX de múltiples fuentes
    """
    files = []
    for root, _, filenames in os.walk(raw_dir):
        for fn in filenames:
            if fn.lower().endswith(".bib"):
                files.append(os.path.join(root, fn))
    files.sort()
    return files

def parse_bib_file(path):
    """
    Parsea archivo BibTeX con estrategia robusta de fallback.
    
    Intenta parseo completo con bibtexparser. Si falla, divide en bloques
    individuales y parsea cada uno. Preserva contenido raw original.
    
    Args:
        path (str): Ruta absoluta al archivo .bib
    
    Returns:
        Tuple[List[dict], Optional[Exception]]:
            - Lista de entradas parseadas (diccionarios con '_raw')
            - Error de parseo si ocurrió, None si parseo exitoso
    
    Estrategia de parseo:
        1. Intenta parseo completo con bibtexparser.loads()
        2. Si exitoso: mapea bloques raw a entradas por ID
        3. Si falla: divide texto en bloques que empiezan con @
        4. Parsea cada bloque individualmente con bibtexparser
        5. Si bloque falla: extrae título con regex y crea entrada mínima
        6. Todas las entradas incluyen campo '_raw' con bloque original
    
    Estructura de entrada retornada:
        {
            'title': str,
            'author': str,
            'year': str,
            ... (otros campos BibTeX)
            '_raw': str  # Bloque BibTeX original
        }
    
    Example:
        >>> entries, error = parse_bib_file("articles.bib")
        >>> len(entries)
        25
        >>> error
        None
        >>> entries[0].keys()
        dict_keys(['title', 'author', 'year', 'ID', '_raw'])
    
    Notas:
        - Maneja archivos malformados con gracia
        - Preserva máxima información posible
        - Útil para archivos BibTeX de múltiples fuentes
        - Encoding UTF-8 con errors='ignore' para caracteres problemáticos
        - Retorna error para diagnóstico pero continúa con fallback
    """
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
    """
    Unifica y deduplica todos los archivos BibTeX de un directorio.
    
    Pipeline completo de procesamiento:
    1. Encuentra todos los .bib recursivamente
    2. Parsea cada archivo con estrategia robusta
    3. Normaliza títulos para detección de duplicados
    4. Separa entradas únicas de duplicadas
    5. Genera archivos de salida preservando formato raw
    6. Reporta estadísticas detalladas del proceso
    
    Args:
        raw_dir (str, optional): Directorio con archivos .bib originales.
                                Default: C:\\Bibliometria\\data\\raw
        processed_dir (str, optional): Directorio de salida.
                                      Default: C:\\Bibliometria\\data\\processed
        out_unique (str, optional): Nombre del archivo de entradas únicas.
                                   Default: "productos_unificados.bib"
        out_duplicates (str, optional): Nombre del archivo de duplicados.
                                       Default: "duplicados.bib"
    
    Returns:
        Dict[str, Any]: Diccionario con estadísticas del proceso:
            - files_found: Lista de archivos .bib encontrados
            - per_folder: Conteo de archivos por carpeta
            - per_file_entries: Entradas por archivo
            - total_entries: Total de entradas procesadas
            - unique_count: Número de entradas únicas
            - duplicates_count: Número de duplicados detectados
            - unique_path: Ruta del archivo unificado
            - dup_path: Ruta del archivo de duplicados
    
    Criterio de deduplicación:
        - Principal: Título normalizado (minúsculas, sin símbolos)
        - Fallback: DOI si no hay título
        - Fallback: ID de la entrada
        - Fallback: Hash del contenido raw
    
    Formato de salida:
        % Fuente: <nombre_archivo>
        @article{clave,
          title = {...},
          ...
        }
    
    Diagnóstico impreso:
        - Resumen por carpeta (número de archivos)
        - Muestra de entradas por archivo (primeros 10)
        - Total de entradas extraídas
        - Errores de parseo detectados
        - Estadísticas de deduplicación
        - Rutas de archivos generados
    
    Example:
        >>> summary = unify_all()
        [INFO] Archivos .bib encontrados: 15
        Resumen por carpeta (nº archivos):
          - acm: 8 archivos
          - sage: 7 archivos
        ...
        [OK] Archivo unificado guardado en: ... (únicos: 324)
        [OK] Archivo de duplicados guardado en: ... (duplicados: 18)
        
        >>> summary['unique_count']
        324
        >>> summary['duplicates_count']
        18
    
    Manejo de errores:
        - Archivos malformados se parsean con fallback
        - Errores se reportan pero no detienen el proceso
        - Entradas sin título usan DOI/ID como identificador
        - Se crea directorio processed si no existe
    
    Notas:
        - Preserva bloques BibTeX originales cuando es posible
        - Genera comentarios con fuente de cada entrada
        - Procesa ACM, SAGE y cualquier otra fuente BibTeX
        - Robusto ante formatos variados y errores de sintaxis
        - Útil para consolidar bibliografía de múltiples búsquedas
    """
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
