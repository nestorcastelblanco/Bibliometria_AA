from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any, Iterable
import sys

import pandas as pd
from .ai_models import SBERTSim, GTESim 

# ---------- FIX IMPORTS: módulo (-m) o ejecución directa ----------
if __package__ is None or __package__ == "":
    PROJECT_ROOT = Path(__file__).resolve().parents[1]  # C:\Bibliometria
    sys.path.append(str(PROJECT_ROOT))
    from requirement_2.classic import LevenshteinSim, DamerauLevenshteinSim, JaccardTokens, CosineTFIDF
    from requirement_2.ai_models import SBERTSim
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    from .classic import LevenshteinSim, DamerauLevenshteinSim, JaccardTokens, CosineTFIDF
    from .ai_models import SBERTSim
# ------------------------------------------------------------------

ROOT_DIR = PROJECT_ROOT
DEFAULT_BIB_FILE = ROOT_DIR / "data" / "processed" / "productos_unificados.bib"
DEFAULT_OUT_FILE = ROOT_DIR / "data" / "processed" / "similitud_req2.json"

# Algoritmos activos (comenta SBERT si no quieres descargar el modelo)
ALGOS = [
    LevenshteinSim(),
    DamerauLevenshteinSim(),
    JaccardTokens(),
    CosineTFIDF(),
    SBERTSim(),
    GTESim()
]

POSSIBLE_ABSTRACT_KEYS = ("abstract", "summary", "annotation", "annote", "notes", "note", "resumen")


def _try_import_bibtexparser():
    try:
        import bibtexparser  # type: ignore
        return bibtexparser
    except Exception:
        return None


def _normalize_field(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    # Quitamos llaves envolventes típicas de BibTeX: { ... }
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1].strip()
    return s


def _fallback_parse_bib(path: Path) -> List[Dict[str, Any]]:
    """
    Parser de emergencia (simple) para .bib cuando no hay bibtexparser.
    Lee entradas por bloques que empiezan con '@' y recoge pares 'clave = {valor}'.
    No soporta todas las complejidades de BibTeX, pero sirve para títulos/abstracts comunes.
    """
    entries: List[Dict[str, Any]] = []
    buf: List[str] = []

    def flush_block(lines: List[str]):
        if not lines:
            return
        block = "\n".join(lines)
        # Extrae pares key = {value} de forma básica
        import re
        fields = dict(re.findall(r'(\w+)\s*=\s*\{(.*?)\}', block, flags=re.DOTALL))
        # Normaliza
        norm = {k.lower(): _normalize_field(v) for k, v in fields.items()}
        entries.append(norm)

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.lstrip().startswith("@"):
                # nuevo bloque
                flush_block(buf)
                buf = [line]
            else:
                buf.append(line)
        # último bloque
        flush_block(buf)

    return entries


def load_bib_dataframe(bib_path: Path = DEFAULT_BIB_FILE) -> pd.DataFrame:
    if not bib_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo .bib en: {bib_path}")

    bibtexparser = _try_import_bibtexparser()
    entries: List[Dict[str, Any]]

    if bibtexparser is not None:
        from bibtexparser.bparser import BibTexParser  # type: ignore
        from bibtexparser.customization import homogenize_latex_encoding  # type: ignore
        with open(bib_path, "r", encoding="utf-8") as bibfile:
            parser = BibTexParser(common_strings=True)
            parser.customization = homogenize_latex_encoding
            db = bibtexparser.load(bibfile, parser=parser)
        entries = db.entries or []
        # Normaliza llaves a lower y limpia braces
        norm_entries = []
        for e in entries:
            ne = {k.lower(): _normalize_field(v) for k, v in e.items()}
            norm_entries.append(ne)
        entries = norm_entries
    else:
        # Parser simple de emergencia
        entries = _fallback_parse_bib(bib_path)

    # Volcar a DataFrame y crear columnas title/abstract
    rows = []
    for e in entries:
        title = _normalize_field(e.get("title", ""))
        abstract = ""
        for k in POSSIBLE_ABSTRACT_KEYS:
            if e.get(k):
                abstract = _normalize_field(e.get(k))
                break
        if not abstract:
            # Fallbacks adicionales (algunos exportadores guardan resumen en 'keywords' o 'description')
            abstract = _normalize_field(e.get("description", e.get("keywords", "")))
        if not abstract:
            # Último recurso: usar el título para que el pipeline no muera (penaliza similitud)
            abstract = title

        authors = e.get("author", e.get("authors", e.get("editor", "")))
        source = e.get("journal", e.get("booktitle", e.get("publisher", e.get("year", ""))))

        rows.append(
            {
                "title": title,
                "abstract": abstract,
                "authors": _normalize_field(authors),
                "source": _normalize_field(source),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"El .bib ({bib_path}) no produjo entradas utilizables (title/abstract).")

    # Asegurar columnas mínimas
    for col in ("title", "abstract"):
        if col not in df.columns:
            df[col] = ""

    return df


def pick_by_indexes(df: pd.DataFrame, idxs: List[int]) -> List[Dict[str, Any]]:
    rows = []
    n = len(df)
    for i in idxs:
        if i < 0 or i >= n:
            raise IndexError(f"Índice {i} fuera de rango (0..{n-1})")
        row = df.iloc[i]
        rows.append(
            {
                "index": int(i),
                "title": row.get("title", ""),
                "abstract": row.get("abstract", ""),
                "authors": row.get("authors", ""),
                "source": row.get("source", ""),
            }
        )
    return rows


def compare_pairs(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            pair = {
                "i": a["index"],
                "j": b["index"],
                "title_i": a["title"],
                "title_j": b["title"],
                "scores": {},
                "explanations": {},
            }
            for algo in ALGOS:
                try:
                    s, exp = algo.compare(a["abstract"], b["abstract"])
                    pair["scores"][algo.name] = float(s)
                    pair["explanations"][algo.name] = exp
                except Exception as e:
                    pair["scores"][algo.name] = None
                    pair["explanations"][algo.name] = {"error": str(e)}
            results.append(pair)
    return results


def run_from_bib(indices: List[int], bib_path: Path | None = None, out_json: Path | None = None) -> str:
    bib = bib_path or DEFAULT_BIB_FILE
    out_path = out_json or DEFAULT_OUT_FILE
    df = load_bib_dataframe(bib)
    rows = pick_by_indexes(df, indices)
    res = compare_pairs(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"selected": rows, "results": res}, f, ensure_ascii=False, indent=2)
    return str(out_path)


def list_titles(bib_path: Path | None = None, limit: int = 20) -> List[str]:
    df = load_bib_dataframe(bib_path or DEFAULT_BIB_FILE)
    limit = min(limit, len(df))
    items = [f"[{i:>4}] {df.iloc[i]['title']}" for i in range(limit)]
    return items


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Req 2: Similitud textual (entradas .bib)")
    parser.add_argument("--bib", type=str, default=str(DEFAULT_BIB_FILE), help="Ruta al .bib (por defecto: data/processed/productos_unificados.bib)")
    parser.add_argument("--out", type=str, default=str(DEFAULT_OUT_FILE), help="Ruta de salida JSON")
    parser.add_argument("--list", type=int, default=0, help="Listar los N primeros títulos con su índice y salir")
    parser.add_argument("indices", nargs="*", type=int, help="Índices a comparar (dos o más)")

    args = parser.parse_args()
    bib_path = Path(args.bib)
    out_path = Path(args.out)

    if args.list and args.list > 0:
        for line in list_titles(bib_path, args.list):
            print(line)
        sys.exit(0)

    if len(args.indices) < 2:
        print("Uso:")
        print("  python -m requirement_2.run_similarity --list 20                  (listar primeros 20 títulos)")
        print("  python -m requirement_2.run_similarity 0 3 7                      (usar .bib por defecto)")
        print("  python -m requirement_2.run_similarity --bib RUTA.bib 0 3 7       (usar .bib específico)")
        sys.exit(1)

    path = run_from_bib(args.indices, bib_path=bib_path, out_json=out_path)
    print(f"OK. Archivo generado: {path}")
