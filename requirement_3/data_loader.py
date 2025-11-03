"""
Módulo de carga y procesamiento de archivos BibTeX para análisis de frecuencia.

Funcionalidades:
- Carga y parseo de archivos .bib con múltiples estrategias (bibtexparser o fallback)
- Extracción de campos clave: title, abstract, authors, source
- Limpieza de comandos LaTeX y normalización de campos
- Conversión a DataFrame de pandas para análisis

Parte del Requerimiento 3: Análisis de frecuencia de términos.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIB = PROJECT_ROOT / "data" / "processed" / "productos_unificados.bib"

POSSIBLE_ABSTRACT_KEYS = ("abstract", "summary", "annotation", "annote", "notes", "note", "resumen")

def _normalize_field(s: Any) -> str:
    """
    Normaliza campo BibTeX eliminando llaves y espacios extra.
    
    Args:
        s (Any): Valor del campo BibTeX
    
    Returns:
        str: Campo normalizado sin llaves ni espacios extra
    
    Example:
        >>> _normalize_field("{Machine Learning}")
        'Machine Learning'
        >>> _normalize_field(None)
        ''
    
    Notas:
        - Convierte None a string vacío
        - Elimina llaves BibTeX externas {...}
        - Limpia espacios al inicio y final
    """
    if s is None: return ""
    x = str(s).strip()
    if x.startswith("{") and x.endswith("}"):  # braces BibTeX
        x = x[1:-1].strip()
    return x

def _fallback_parse_bib(path: Path) -> List[Dict[str, Any]]:
    """
    Parser alternativo de BibTeX sin dependencia de bibtexparser.
    
    Implementa parseo básico de archivos .bib usando regex cuando
    la librería bibtexparser no está disponible.
    
    Args:
        path (Path): Ruta al archivo .bib
    
    Returns:
        List[Dict[str, Any]]: Lista de entradas parseadas como diccionarios
    
    Process:
        1. Lee archivo línea por línea
        2. Identifica entradas por líneas que empiezan con '@'
        3. Extrae campos usando regex: campo = {valor}
        4. Normaliza cada campo con _normalize_field
        5. Retorna lista de diccionarios con claves en minúsculas
    
    Notas:
        - Fallback cuando bibtexparser falla o no está instalado
        - Menos robusto que bibtexparser pero cubre casos comunes
        - Usa regex DOTALL para capturar valores multilínea
        - Convierte todas las claves a minúsculas para consistencia
    """
    # Parser simple si no hay bibtexparser
    entries = []
    buf: List[str] = []
    def flush(lines: List[str]):
        if not lines: return
        import re
        block = "\n".join(lines)
        fields = dict(re.findall(r'(\w+)\s*=\s*\{(.*?)\}', block, flags=re.DOTALL))
        entries.append({k.lower(): _normalize_field(v) for k, v in fields.items()})
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.lstrip().startswith("@"):
                flush(buf); buf = [line]
            else:
                buf.append(line)
        flush(buf)
    return entries

def load_bib_dataframe(bib_path: Path = DEFAULT_BIB) -> pd.DataFrame:
    """
    Carga archivo BibTeX y convierte a DataFrame con campos procesados.
    
    Lee archivo .bib, extrae campos clave (title, abstract, authors, source),
    limpia comandos LaTeX, y construye DataFrame listo para análisis.
    
    Args:
        bib_path (Path, optional): Ruta al archivo .bib. 
                                   Default: data/processed/productos_unificados.bib
    
    Returns:
        pd.DataFrame: DataFrame con columnas ['title', 'abstract', 'authors', 'source']
    
    Raises:
        FileNotFoundError: Si el archivo .bib no existe
        ValueError: Si el .bib no contiene entradas válidas
    
    Process:
        1. Intenta cargar con bibtexparser (preferido)
        2. Si falla, usa parser fallback regex
        3. Extrae y normaliza campos por entrada:
           - title: campo 'title'
           - abstract: busca en POSSIBLE_ABSTRACT_KEYS, fallback a description/keywords/title
           - authors: campo 'author', 'authors' o 'editor'
           - source: campo 'journal', 'booktitle', 'publisher' o 'year'
        4. Limpia comandos LaTeX y llaves residuales
        5. Construye DataFrame y valida no esté vacío
    
    Campos alternativos para abstract:
        abstract, summary, annotation, annote, notes, note, resumen
    
    Limpieza LaTeX:
        - Elimina comandos \\comando
        - Elimina llaves {}
        - Normaliza espacios múltiples
    
    Example:
        >>> df = load_bib_dataframe()
        >>> df.columns
        Index(['title', 'abstract', 'authors', 'source'], dtype='object')
        >>> len(df) > 0
        True
    
    Notas:
        - Usa bibtexparser con homogenize_latex_encoding si está disponible
        - Fallback a parser regex simple si bibtexparser falla
        - Todos los campos se limpian de LaTeX para texto plano
        - Abstract usa múltiples fallbacks para maximizar cobertura
    """
    if not bib_path.exists():
        raise FileNotFoundError(f"No se encontró el .bib: {bib_path}")
    try:
        import bibtexparser
        from bibtexparser.bparser import BibTexParser
        from bibtexparser.customization import homogenize_latex_encoding
        with open(bib_path, "r", encoding="utf-8") as bibfile:
            parser = BibTexParser(common_strings=True)
            parser.customization = homogenize_latex_encoding
            db = bibtexparser.load(bibfile, parser=parser)
        raw = db.entries or []
        entries = [{k.lower(): _normalize_field(v) for k, v in e.items()} for e in raw]
    except Exception:
        entries = _fallback_parse_bib(bib_path)

    rows = []
    for e in entries:
        title = _normalize_field(e.get("title", ""))
        # quitar comandos LaTeX y llaves residuales
        def clean_tex(t: str) -> str:
            t = re.sub(r"\\[a-zA-Z]+", " ", t)
            t = re.sub(r"[{}]", " ", t)
            return re.sub(r"\s+", " ", t).strip()
        title = clean_tex(title)
        abstract = ""
        for k in POSSIBLE_ABSTRACT_KEYS:
            if e.get(k):
                abstract = clean_tex(_normalize_field(e.get(k)))
                break
        if not abstract:
            abstract = clean_tex(_normalize_field(e.get("description", e.get("keywords", "")))) or title
        authors = clean_tex(_normalize_field(e.get("author", e.get("authors", e.get("editor", "")))))
        source = clean_tex(_normalize_field(e.get("journal", e.get("booktitle", e.get("publisher", e.get("year", ""))))))
        rows.append({"title": title, "abstract": abstract, "authors": authors, "source": source})
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("El .bib no produjo entradas con title/abstract utilizables.")
    return df
