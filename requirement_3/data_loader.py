from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIB = PROJECT_ROOT / "data" / "processed" / "productos_unificados.bib"

POSSIBLE_ABSTRACT_KEYS = ("abstract", "summary", "annotation", "annote", "notes", "note", "resumen")

def _normalize_field(s: Any) -> str:
    if s is None: return ""
    x = str(s).strip()
    if x.startswith("{") and x.endswith("}"):  # braces BibTeX
        x = x[1:-1].strip()
    return x

def _fallback_parse_bib(path: Path) -> List[Dict[str, Any]]:
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
