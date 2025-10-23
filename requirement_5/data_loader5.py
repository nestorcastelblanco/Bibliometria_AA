from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import re
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIB = PROJECT_ROOT / "data" / "processed" / "productos_unificados.bib"

# Campos posibles
ABSTRACT_KEYS = ("abstract","summary","annotation","annote","notes","note","resumen")
KEYWORD_KEYS  = ("keywords","keyword","tags")
AFFIL_KEYS    = ("affiliation","affiliations","address","institution","organization","school")
COUNTRY_KEYS  = ("country","location","nation")

def _normalize_field(s: Any) -> str:
    if s is None: return ""
    x = str(s).strip()
    if x.startswith("{") and x.endswith("}"): x = x[1:-1].strip()
    # quitar comandos LaTeX/llaves restantes
    x = re.sub(r"\\[a-zA-Z]+", " ", x)
    x = re.sub(r"[{}]", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x

def _fallback_parse_bib(path: Path) -> List[Dict[str, Any]]:
    entries = []
    buf: List[str] = []
    def flush(lines: List[str]):
        if not lines: return
        block = "\n".join(lines)
        fields = dict(re.findall(r'(\w+)\s*=\s*\{(.*?)\}', block, flags=re.DOTALL))
        entries.append({k.lower(): _normalize_field(v) for k,v in fields.items()})
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.lstrip().startswith("@"):
                flush(buf); buf=[line]
            else:
                buf.append(line)
        flush(buf)
    return entries

def load_bib_dataframe(bib_path: Path = DEFAULT_BIB) -> pd.DataFrame:
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
        title   = _normalize_field(e.get("title", ""))
        year    = _normalize_field(e.get("year", ""))
        journal = _normalize_field(e.get("journal", e.get("booktitle", "")))
        authors = _normalize_field(e.get("author", e.get("authors","")))
        # abstract
        abstract = ""
        for k in ABSTRACT_KEYS:
            if e.get(k): abstract = _normalize_field(e.get(k)); break
        # keywords
        keywords = ""
        for k in KEYWORD_KEYS:
            if e.get(k): keywords = _normalize_field(e.get(k)); break
        # affiliation / country
        affiliation = ""
        for k in AFFIL_KEYS:
            if e.get(k): affiliation = _normalize_field(e.get(k)); break
        country = ""
        for k in COUNTRY_KEYS:
            if e.get(k): country = _normalize_field(e.get(k)); break

        rows.append({
            "title": title, "year": year, "journal": journal, "authors": authors,
            "abstract": abstract, "keywords": keywords,
            "affiliation": affiliation, "country": country
        })
    df = pd.DataFrame(rows)
    return df
