# requirement_2/console_report.py
from __future__ import annotations
import json, argparse
from pathlib import Path
from typing import Any, Dict, List, Optional
import statistics as stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = PROJECT_ROOT / "data" / "processed" / "similitud_req2.json"

PRIMARY_ORDER = [
    "GTE (coseno)",
    "SBERT (coseno)",
    "Coseno (TF-IDF)",
    "Jaccard (tokens)",
    "Damerau–Levenshtein (normalizada)",
    "Levenshtein (normalizada)",
]

def pct(x: Optional[float]) -> str:
    return "—" if x is None else f"{x*100:,.1f}%"

def read_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_algo(results: List[Dict[str, Any]], prefer: Optional[str]) -> str:
    if prefer:
        if any(prefer in r.get("scores", {}) for r in results):
            return prefer
    for cand in PRIMARY_ORDER:
        if any(cand in r.get("scores", {}) for r in results):
            return cand
    # fallback
    for r in results:
        if r.get("scores"):
            return list(r["scores"].keys())[0]
    raise ValueError("No se encontraron algoritmos en los resultados.")

def flat_scores(results: List[Dict[str, Any]], algo: str) -> List[float]:
    vals = []
    for r in results:
        s = r["scores"].get(algo)
        if s is not None:
            vals.append(float(s))
    return vals

def compute_stats(vals: List[float]) -> Dict[str, Any]:
    if not vals:
        return {"n": 0, "min": None, "max": None, "mean": None, "median": None}
    return {
        "n": len(vals),
        "min": min(vals),
        "max": max(vals),
        "mean": sum(vals)/len(vals),
        "median": stats.median(vals),
    }

def buckets(vals: List[float]) -> Dict[str, int]:
    b = {"≥0.80":0, "0.60–0.79":0, "0.40–0.59":0, "0.20–0.39":0, "<0.20":0}
    for v in vals:
        if v >= 0.80: b["≥0.80"] += 1
        elif v >= 0.60: b["0.60–0.79"] += 1
        elif v >= 0.40: b["0.40–0.59"] += 1
        elif v >= 0.20: b["0.20–0.39"] += 1
        else: b["<0.20"] += 1
    return b

def rank(results: List[Dict[str, Any]], algo: str, top: int) -> List[Dict[str, Any]]:
    ranked = sorted(results, key=lambda r: (r["scores"].get(algo) or 0.0), reverse=True)
    return ranked[:min(top, len(ranked))]

def main():
    ap = argparse.ArgumentParser(
        description="Resumen en consola del Requerimiento 2 (porcentajes, ranking y estadísticas)."
    )
    ap.add_argument("--json", default=str(DEFAULT_JSON), help="Ruta a similitud_req2.json")
    ap.add_argument("--algo", default=None, help="Algoritmo principal (si se omite, se elige automáticamente)")
    ap.add_argument("--top", type=int, default=10, help="Cantidad de pares a mostrar")
    args = ap.parse_args()

    data = read_json(Path(args.json))
    selected = data.get("selected", [])
    results  = data.get("results", [])
    if not results:
        print("No hay resultados en el JSON. Ejecuta primero requirement_2.run_similarity.")
        return

    algo = detect_algo(results, args.algo)
    vals = flat_scores(results, algo)
    st = compute_stats(vals)
    dist = buckets(vals)
    topN = rank(results, algo, args.top)

    # ===== Salida en consola =====
    print("\n================= Requerimiento 2 — Resumen =================")
    print(f"Algoritmo principal: {algo}")
    print(f"Artículos seleccionados: {[it['index'] for it in selected]}")
    print(f"Pares comparados: {len(results)}")
    print("--------------------------------------------------------------")
    print(f"Estadísticas →  media: {pct(st['mean'])} | mediana: {pct(st['median'])} "
          f"| min: {pct(st['min'])} | max: {pct(st['max'])}")
    print("Distribución:")
    print(f"  ≥0.80: {dist['≥0.80']},  0.60–0.79: {dist['0.60–0.79']},  0.40–0.59: {dist['0.40–0.59']},  "
          f"0.20–0.39: {dist['0.20–0.39']},  <0.20: {dist['<0.20']}")
    print("--------------------------------------------------------------")
    print(f"Top {len(topN)} pares por {algo}:")
    for i, r in enumerate(topN, 1):
        s = r["scores"].get(algo)
        t1 = (r.get("title_i") or "").strip().replace("\n", " ")
        t2 = (r.get("title_j") or "").strip().replace("\n", " ")
        print(f"{i:>2}. ({r['i']},{r['j']})  {pct(s)}")
        print(f"    • {t1}")
        print(f"    • {t2}")
    print("==============================================================\n")

if __name__ == "__main__":
    main()
