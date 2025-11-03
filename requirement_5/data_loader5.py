"""
Módulo de carga de datos bibliográficos para análisis visual (Requerimiento 5).

Parsea archivos BibTeX y extrae campos relevantes para visualizaciones:
- Metadatos: título, año, journal, autores
- Contenido: abstract, keywords
- Geográficos: affiliations, países

Maneja múltiples variantes de nombres de campos BibTeX y limpia formato LaTeX.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import re
import pandas as pd

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIB = PROJECT_ROOT / "data" / "processed" / "productos_unificados.bib"

# Mapeo de variantes de campos BibTeX
ABSTRACT_KEYS = ("abstract", "summary", "annotation", "annote", "notes", "note", "resumen")
KEYWORD_KEYS  = ("keywords", "keyword", "tags")
AFFIL_KEYS    = ("affiliation", "affiliations", "address", "institution", "organization", "school")
COUNTRY_KEYS  = ("country", "location", "nation")

def _normalize_field(s: Any) -> str:
    """
    Normaliza un campo BibTeX eliminando formato LaTeX y limpiando espacios.
    
    Realiza las siguientes transformaciones:
    1. Remueve llaves BibTeX externas {...}
    2. Elimina comandos LaTeX (\\textbf, \\emph, etc.)
    3. Remueve llaves remanentes
    4. Normaliza espacios en blanco
    
    Args:
        s (Any): Campo a normalizar (puede ser str, None, o cualquier tipo)
    
    Returns:
        str: Texto limpio y normalizado, string vacío si input es None
    
    Example:
        >>> _normalize_field("{\\textbf{Machine Learning}}")
        'Machine Learning'
        >>> _normalize_field("Normal  text   with    spaces")
        'Normal text with spaces'
    """
    if s is None: 
        return ""
    
    x = str(s).strip()
    
    # Remover llaves externas de BibTeX
    if x.startswith("{") and x.endswith("}"): 
        x = x[1:-1].strip()
    
    # Quitar comandos LaTeX (e.g., \textbf, \emph, \cite)
    x = re.sub(r"\\[a-zA-Z]+", " ", x)
    
    # Remover llaves restantes
    x = re.sub(r"[{}]", " ", x)
    
    # Normalizar espacios múltiples
    x = re.sub(r"\s+", " ", x).strip()
    
    return x

def _fallback_parse_bib(path: Path) -> List[Dict[str, Any]]:
    """
    Parser simple de BibTeX como alternativa si bibtexparser no está disponible.
    
    Usa regex para extraer campos básicos de entradas BibTeX. Es menos robusto
    que bibtexparser pero funciona sin dependencias externas.
    
    Args:
        path (Path): Ruta al archivo .bib
    
    Returns:
        List[Dict[str, Any]]: Lista de diccionarios con campos normalizados
    
    Formato esperado:
        @article{key,
            field1 = {value1},
            field2 = {value2}
        }
    
    Notas:
        - Detecta inicio de entrada por líneas que empiezan con '@'
        - Extrae pares campo=valor con regex
        - Normaliza todos los valores con _normalize_field()
        - Convierte nombres de campo a minúsculas
    """
    entries = []
    buf: List[str] = []
    
    def flush(lines: List[str]):
        """Procesa buffer acumulado como una entrada BibTeX."""
        if not lines: 
            return
        block = "\n".join(lines)
        # Extraer campos: campo = {valor}
        fields = dict(re.findall(r'(\w+)\s*=\s*\{(.*?)\}', block, flags=re.DOTALL))
        entries.append({k.lower(): _normalize_field(v) for k, v in fields.items()})
    
    # Leer archivo línea por línea
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.lstrip().startswith("@"):
                # Nueva entrada: procesar buffer previo
                flush(buf)
                buf = [line]
            else:
                buf.append(line)
        # Procesar última entrada
        flush(buf)
    
    return entries

def load_bib_dataframe(bib_path: Path = DEFAULT_BIB) -> pd.DataFrame:
    """
    Carga archivo BibTeX como DataFrame de pandas para análisis visual.
    
    Intenta usar bibtexparser profesional primero, recurre a parser simple
    si no está disponible. Extrae campos clave manejando múltiples variantes
    de nombres de campos BibTeX.
    
    Args:
        bib_path (Path): Ruta al archivo .bib (default: productos_unificados.bib)
    
    Returns:
        pd.DataFrame: DataFrame con columnas:
            - title: Título del artículo
            - year: Año de publicación
            - journal: Journal o booktitle de la conferencia
            - authors: Lista de autores
            - abstract: Resumen del artículo
            - keywords: Palabras clave
            - affiliation: Institución/afiliación
            - country: País de la institución
    
    Raises:
        FileNotFoundError: Si el archivo .bib no existe
    
    Proceso:
        1. Intenta cargar con bibtexparser (más robusto)
        2. Si falla, usa _fallback_parse_bib() (más simple)
        3. Normaliza todos los campos con _normalize_field()
        4. Busca campos en múltiples variantes (abstract/summary/resumen)
        5. Construye DataFrame con estructura uniforme
    
    Notas:
        - Maneja variantes de campos: abstract/summary, keywords/tags, etc.
        - Limpia formato LaTeX automáticamente
        - Convierte todos los campos a minúsculas
        - Campos faltantes se dejan como string vacío
    
    Example:
        >>> df = load_bib_dataframe()
        >>> print(df.columns)
        Index(['title', 'year', 'journal', 'authors', 'abstract', 
               'keywords', 'affiliation', 'country'], dtype='object')
        >>> print(len(df))
        1196
    """
    if not bib_path.exists():
        raise FileNotFoundError(f"No se encontró el .bib: {bib_path}")
    
    # === PASO 1: Parsear archivo BibTeX ===
    try:
        # Intento con bibtexparser profesional
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
        # Fallback a parser simple si bibtexparser no está disponible
        entries = _fallback_parse_bib(bib_path)

    # === PASO 2: Extraer campos relevantes con variantes ===
    rows = []
    for e in entries:
        # Campos básicos
        title   = _normalize_field(e.get("title", ""))
        year    = _normalize_field(e.get("year", ""))
        journal = _normalize_field(e.get("journal", e.get("booktitle", "")))
        authors = _normalize_field(e.get("author", e.get("authors", "")))
        
        # Abstract (buscar en múltiples variantes)
        abstract = ""
        for k in ABSTRACT_KEYS:
            if e.get(k): 
                abstract = _normalize_field(e.get(k))
                break
        
        # Keywords (buscar en múltiples variantes)
        keywords = ""
        for k in KEYWORD_KEYS:
            if e.get(k): 
                keywords = _normalize_field(e.get(k))
                break
        
        # Affiliation (buscar en múltiples variantes)
        affiliation = ""
        for k in AFFIL_KEYS:
            if e.get(k): 
                affiliation = _normalize_field(e.get(k))
                break
        
        # Country (buscar en múltiples variantes)
        country = ""
        for k in COUNTRY_KEYS:
            if e.get(k): 
                country = _normalize_field(e.get(k))
                break

        rows.append({
            "title": title, 
            "year": year, 
            "journal": journal, 
            "authors": authors,
            "abstract": abstract, 
            "keywords": keywords,
            "affiliation": affiliation, 
            "country": country
        })
    
    # === PASO 3: Construir DataFrame ===
    df = pd.DataFrame(rows)
    return df
