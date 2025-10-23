from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import statistics as stats
import argparse
import csv
from requirement_2.explainers import appendix_markdown

# Rutas robustas
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = PROJECT_ROOT / "data" / "processed" / "similitud_req2.json"
DEFAULT_MD   = PROJECT_ROOT / "data" / "processed" / "reporte_similitud.md"
DEFAULT_CSV  = PROJECT_ROOT / "data" / "processed" / "reporte_similitud_top.csv"

# Prioridad de “algoritmo principal” si no se especifica --algo
PRIMARY_ORDER = [
    "GTE (coseno)",
    "SBERT (coseno)",
    "Coseno (TF-IDF)",
    "Jaccard (tokens)",
    "Damerau–Levenshtein (normalizada)",
    "Levenshtein (normalizada)",
]

def _pct(x: Optional[float]) -> str:
    if x is None:
        return "—"
    return f"{x*100:,.1f}%"

def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el JSON: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _detect_primary_algo(results: List[Dict[str, Any]], prefer: Optional[str]) -> str:
    # Si el usuario especifica y existe, usarlo
    if prefer:
        # verificar existencia en algún result
        for r in results:
            if prefer in r.get("scores", {}):
                return prefer
        # si no existe, seguimos a autoselección
    # Autoselección: primer algoritmo de PRIMARY_ORDER presente en results
    for candidate in PRIMARY_ORDER:
        for r in results:
            if candidate in r.get("scores", {}):
                return candidate
    # Fallback: cualquier clave que exista
    for r in results:
        sc = r.get("scores", {})
        if sc:
            return list(sc.keys())[0]
    raise ValueError("No se encuentran algoritmos de similitud en 'results'.")

def _flat_scores_for_algo(results: List[Dict[str, Any]], algo: str) -> List[float]:
    vals = []
    for r in results:
        s = r["scores"].get(algo)
        if s is not None:
            vals.append(float(s))
    return vals

def _stats(vals: List[float]) -> Dict[str, Any]:
    if not vals:
        return {"n": 0, "min": None, "max": None, "mean": None, "median": None}
    return {
        "n": len(vals),
        "min": min(vals),
        "max": max(vals),
        "mean": sum(vals) / len(vals),
        "median": stats.median(vals),
    }

def _bucket_counts(vals: List[float]) -> Dict[str, int]:
    # buckets por similitud (cos/sbert/jaccard ~ [0,1])
    buckets = {
        "≥0.80": 0,
        "0.60–0.79": 0,
        "0.40–0.59": 0,
        "0.20–0.39": 0,
        "<0.20": 0,
    }
    for v in vals:
        if v >= 0.80: buckets["≥0.80"] += 1
        elif v >= 0.60: buckets["0.60–0.79"] += 1
        elif v >= 0.40: buckets["0.40–0.59"] += 1
        elif v >= 0.20: buckets["0.20–0.39"] += 1
        else: buckets["<0.20"] += 1
    return buckets

def _rank(results: List[Dict[str, Any]], algo: str, top: int) -> List[Dict[str, Any]]:
    ranked = sorted(
        results,
        key=lambda r: (r["scores"].get(algo) or 0.0),
        reverse=True
    )
    return ranked[:top]

def _safe_get(d: Dict[str, Any], *keys, default: str = "") -> str:
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return str(cur)

def generate_markdown(data: Dict[str, Any], algo: str, top: int, out_md: Path):
    selected = data.get("selected", [])
    results = data.get("results", [])

    vals = _flat_scores_for_algo(results, algo)
    s = _stats(vals)
    buckets = _bucket_counts(vals)
    ranked = _rank(results, algo, min(top, len(results)))

    # Encabezado y contexto
    md = []
    md.append("# Reporte de Similitud Textual")
    md.append("")
    md.append(f"**Algoritmo principal:** {algo}")
    md.append(f"**Pares totales:** {len(results)}")
    md.append("")
    md.append("## Selección de artículos")
    for item in selected:
        md.append(f"- [{item['index']}] {item.get('title','').strip()}")
    md.append("")

    # Resumen estadístico
    md.append("## Estadísticas generales")
    md.append("")
    md.append("| Métrica | Valor |")
    md.append("|---|---:|")
    md.append(f"| n | {s['n']} |")
    md.append(f"| min | {_pct(s['min']) if s['min'] is not None else '—'} |")
    md.append(f"| max | {_pct(s['max']) if s['max'] is not None else '—'} |")
    md.append(f"| media | {_pct(s['mean']) if s['mean'] is not None else '—'} |")
    md.append(f"| mediana | {_pct(s['median']) if s['median'] is not None else '—'} |")
    md.append("")

    md.append("### Distribución por rangos")
    md.append("")
    md.append("| Rango | Conteo |")
    md.append("|---|---:|")
    for k, v in buckets.items():
        md.append(f"| {k} | {v} |")
    md.append("")

    # Top pares
    md.append(f"## Top {len(ranked)} pares por {algo}")
    md.append("")
    md.append("| Rank | Índices (i,j) | % Similitud | Título i | Título j |")
    md.append("|---:|:---:|---:|---|---|")
    for idx, r in enumerate(ranked, 1):
        score = r["scores"].get(algo)
        md.append(
            f"| {idx} | {r['i']},{r['j']} | {_pct(score)} | "
            f"{_safe_get(r, 'title_i').strip()} | {_safe_get(r, 'title_j').strip()} |"
        )
    md.append("")

    # Tabla comparativa por algoritmo (si quieres panorama completo)
    md.append("## Comparación de algoritmos (para los Top anteriores)")
    md.append("")
    # Detectar todos los algoritmos presentes (unión de claves)
    algos_all = []
    for r in results:
        for k in r.get("scores", {}).keys():
            if k not in algos_all:
                algos_all.append(k)
    md.append("| i,j | " + " | ".join(algos_all) + " |")
    md.append("|:--:|" + "|".join([":--:" for _ in algos_all]) + "|")
    for r in ranked:
        row = [f"{r['i']},{r['j']}"]
        for a in algos_all:
            row.append(_pct(r["scores"].get(a)))
        md.append("| " + " | ".join(row) + " |")
    md.append("")
    
    md.append(appendix_markdown())
    
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md), encoding="utf-8")

def generate_csv_top(data: Dict[str, Any], algo: str, top: int, out_csv: Path):
    results = data.get("results", [])
    ranked = _rank(results, algo, min(top, len(results)))
    # columnas
    fieldnames = ["rank", "i", "j", "score", "score_pct", "title_i", "title_j"]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for idx, r in enumerate(ranked, 1):
            s = r["scores"].get(algo)
            w.writerow({
                "rank": idx,
                "i": r["i"],
                "j": r["j"],
                "score": f"{s:.6f}" if s is not None else "",
                "score_pct": _pct(s),
                "title_i": _safe_get(r, "title_i"),
                "title_j": _safe_get(r, "title_j"),
            })

def print_console_summary(data: Dict[str, Any], algo: str, top: int):
    results = data.get("results", [])
    selected = data.get("selected", [])
    vals = _flat_scores_for_algo(results, algo)
    s = _stats(vals)
    print("\n=== Resumen de Similitud ===")
    print(f"Algoritmo principal: {algo}")
    print(f"Artículos seleccionados: {[it['index'] for it in selected]}")
    print(f"Pares: {len(results)}  |  media={_pct(s['mean']) if s['mean'] is not None else '—'}  "
          f"mediana={_pct(s['median']) if s['median'] is not None else '—'}  "
          f"min={_pct(s['min']) if s['min'] is not None else '—'}  max={_pct(s['max']) if s['max'] is not None else '—'}")

    ranked = _rank(results, algo, min(top, len(results)))
    print(f"\nTop {len(ranked)} pares por {algo}:")
    for idx, r in enumerate(ranked, 1):
        s = r["scores"].get(algo)
        print(f"{idx:>2}. ({r['i']},{r['j']})  {_pct(s)}  |  {r['title_i'][:60]}  <>  {r['title_j'][:60]}")

def main():
    p = argparse.ArgumentParser(description="Genera reporte legible de similitud (porcentajes, ranking y estadísticas).")
    p.add_argument("--json", type=str, default=str(DEFAULT_JSON), help="Ruta al similitud_req2.json")
    p.add_argument("--md", type=str, default=str(DEFAULT_MD), help="Ruta de salida Markdown")
    p.add_argument("--csv", type=str, default=str(DEFAULT_CSV), help="Ruta de salida CSV TOP")
    p.add_argument("--top", type=int, default=10, help="Cantidad de pares a mostrar")
    p.add_argument("--algo", type=str, default=None, help="Algoritmo principal (si omites, se elige automáticamente)")
    args = p.parse_args()

    data = _read_json(Path(args.json))
    results = data.get("results", [])
    if not results:
        raise ValueError("El JSON no contiene pares en 'results'.")

    algo = _detect_primary_algo(results, args.algo)
    print_console_summary(data, algo, args.top)
    generate_markdown(data, algo, args.top, Path(args.md))
    generate_csv_top(data, algo, args.top, Path(args.csv))
    print(f"\nArchivos generados:\n- {args.md}\n- {args.csv}")

if __name__ == "__main__":
    main()
