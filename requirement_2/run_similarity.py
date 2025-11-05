from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Tuple
import json, csv, itertools

PROJECT_ROOT = Path(__file__).resolve().parents[1]
THIS_DIR     = Path(__file__).resolve().parent
OUT_JSON     = PROJECT_ROOT / "data" / "processed" / "similitud_req2.json"

def _maybe_import(mod: str):
    try:
        return __import__(mod, fromlist=['*'])
    except Exception:
        return None

classic      = _maybe_import("requirement_2.classic")
ai_models    = _maybe_import("requirement_2.ai_models")
dl3          = _maybe_import("requirement_3.data_loader")

def _best_text(rec: Dict[str, Any]) -> str:
    for k in ["abstract","Resumen","resumen","summary","Summary","abstractText","abstract_note"]:
        v = (rec.get(k) or "").strip()
        if v:
            return v
    title = (rec.get("title") or rec.get("Title") or "").strip()
    kws   = rec.get("keywords") or rec.get("Keywords") or ""
    if isinstance(kws, list):
        kws = ", ".join(kws)
    return (" ".join([title, str(kws or "")])).strip()

def _title(rec: Dict[str, Any]) -> str:
    return (rec.get("title") or rec.get("Title") or "").strip()

def _load_from_unificado_csv() -> List[Dict[str, Any]]:
    candidates = [
        PROJECT_ROOT / "requirement_1" / "data" / "productos_unificados.csv",
        PROJECT_ROOT / "data" / "productos_unificados.csv",
        PROJECT_ROOT / "data" / "unificado.csv",
    ]
    for p in candidates:
        if p.exists():
            with p.open("r", encoding="utf-8", newline="") as f:
                return list(csv.DictReader(f))
    return []

def _load_from_req3_json() -> List[Dict[str, Any]]:
    candidates = [
        PROJECT_ROOT / "requirement_3" / "req3_resultados.json",
        PROJECT_ROOT / "data" / "processed" / "req3_resultados.json",
    ]
    for p in candidates:
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                recs = data.get("records") or data.get("docs") or data.get("items") or []
                if isinstance(recs, list) and recs:
                    return recs
            if isinstance(data, list):
                return data
    return []

def _load_from_bib_default() -> List[Dict[str, Any]]:
    """
    Carga DEFAULT_BIB de requirement_3.data_loader; compatible con varias versiones de bibtexparser.
    """
    if dl3 is None or not hasattr(dl3, "DEFAULT_BIB"):
        raise FileNotFoundError("No se encontró DEFAULT_BIB en requirement_3.data_loader.")
    bib_path = Path(getattr(dl3, "DEFAULT_BIB"))
    if not bib_path.exists():
        raise FileNotFoundError(f"No existe el .bib esperado: {bib_path}")

    try:
        import bibtexparser
    except Exception as e:
        raise RuntimeError("Debes instalar 'bibtexparser' (pip install bibtexparser).") from e

    db = None
    # 1) API moderna
    try:
        with open(bib_path, "r", encoding="utf-8") as f:
            db = bibtexparser.load(f)  # type: ignore[attr-defined]
    except Exception:
        # 2) Parser explícito
        try:
            from bibtexparser.bparser import BibTexParser
            parser = BibTexParser(common_strings=True)
            with open(bib_path, "r", encoding="utf-8") as f:
                db = bibtexparser.load(f, parser=parser)  # type: ignore[attr-defined]
        except Exception:
            # 3) Último recurso
            with open(bib_path, "r", encoding="utf-8") as f:
                content = f.read()
            db = bibtexparser.loads(content)  # type: ignore[attr-defined]

    entries = getattr(db, "entries", None)
    if entries is None:
        entries_dict = getattr(db, "entries_dict", None)
        if isinstance(entries_dict, dict):
            entries = list(entries_dict.values())
    if not entries:
        raise ValueError(f"No se extrajeron entradas desde {bib_path}.")
    return entries

def _load_corpus_records(force_bib: bool=False) -> Tuple[List[str], List[str]]:
    recs: List[Dict[str, Any]] = []
    if not force_bib:
        recs = _load_from_unificado_csv()
        if not recs:
            recs = _load_from_req3_json()
    if not recs:
        recs = _load_from_bib_default()
    abstracts = [_best_text(r) for r in recs]
    titles    = [_title(r) for r in recs]
    return abstracts, titles

def _discover_algorithms():
    algos = []
    def _add(cls_name, mod):
        if mod is None:
            return
        cls = getattr(mod, cls_name, None)
        if cls is None:
            return
        try:
            inst = cls()
            name = getattr(inst, "name", cls_name)
            algos.append((name, inst.score))
        except Exception:
            pass
    _add("LevenshteinSim", classic)
    _add("DamerauLevenshteinSim", classic)
    _add("JaccardTokens", classic)
    _add("CosineTFIDF", classic)
    _add("SBERTSim", ai_models)
    _add("GTESim",  ai_models)
    return algos

def _compute(indices: List[int], texts: List[str], titles: List[str]) -> Dict[str, Any]:
    pairs = list(itertools.combinations(indices, 2))
    algos = _discover_algorithms()
    if not algos:
        raise RuntimeError("No se encontraron algoritmos en requirement_2.classic / ai_models.")

    results = []
    for (i, j) in pairs:
        a, b = texts[i], texts[j]
        scores = {}
        for name, fn in algos:
            try:
                scores[name] = float(fn(a, b))
            except Exception:
                scores[name] = None
        results.append({
            "i": i, "j": j,
            "scores": scores,
            "title_i": titles[i] if i < len(titles) else "",
            "title_j": titles[j] if j < len(titles) else "",
        })

    data = {
        "selected": [{"index": k, "title": titles[k] if k < len(titles) else ""} for k in indices],
        "results": results
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

def run(indices: List[int]) -> Path:
    if not indices or len(indices) < 2:
        raise ValueError("Se requieren ≥2 índices, ej.: [0, 3, 7].")
    texts, titles = _load_corpus_records(force_bib=False)
    if max(indices) >= len(texts):
        raise IndexError(f"Índice fuera de rango. Corpus={len(texts)}, max_idx={max(indices)}")
    _compute(indices, texts, titles)
    return OUT_JSON

def run_from_bib(indices: List[int]) -> Path:
    if not indices or len(indices) < 2:
        raise ValueError("Se requieren ≥2 índices, ej.: [0, 3, 7].")
    texts, titles = _load_corpus_records(force_bib=True)
    if max(indices) >= len(texts):
        raise IndexError(f"Índice fuera de rango. Corpus={len(texts)}, max_idx={max(indices)}")
    _compute(indices, texts, titles)
    return OUT_JSON
