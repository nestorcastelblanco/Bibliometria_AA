from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse

from requirement_3.data_loader import load_bib_dataframe, DEFAULT_BIB, PROJECT_ROOT
from requirement_3.frequency import normalize_terms, term_frequencies_per_doc, aggregate_frequencies
from requirement_3.auto_terms import extract_auto_terms
from requirement_3.evaluate import precision_against_seeds
from requirement_3.keywords import CATEGORY_NAME, SEED_WORDS

OUT_JSON = PROJECT_ROOT / "requirement_3" / "req3_resultados.json"

def run_req3(
    bib_path: Path = DEFAULT_BIB,
    max_auto_terms: int = 15,
    min_df: int = 2,
    threshold: float = 0.50
) -> str:
    df = load_bib_dataframe(bib_path)
    abstracts = [str(x) for x in df["abstract"].tolist()]
    # 1) Frecuencias de SEED_WORDS
    seeds_norm = normalize_terms(SEED_WORDS)
    per_doc = term_frequencies_per_doc(abstracts, seeds_norm)
    agg = aggregate_frequencies(per_doc)

    # 2) Términos auto-generados (máx. 15) por TF-IDF
    auto_terms = extract_auto_terms(abstracts, max_terms=max_auto_terms, min_df=min_df)

    # 3) Frecuencia de términos auto-generados
    auto_per_doc = term_frequencies_per_doc(abstracts, auto_terms)
    auto_agg = aggregate_frequencies(auto_per_doc)

    # 4) Precisión de términos auto-generados vs. semillas (embeddings)
    eval_res = precision_against_seeds(auto_terms, seeds_norm, threshold=threshold)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "category": CATEGORY_NAME,
        "seed_words_original": SEED_WORDS,
        "seed_words_normalized": seeds_norm,
        "freq_per_doc_seeds": per_doc,
        "freq_total_seeds": agg,
        "auto_terms": auto_terms,
        "freq_per_doc_auto": auto_per_doc,
        "freq_total_auto": auto_agg,
        "evaluation": eval_res,
        "params": {"max_auto_terms": max_auto_terms, "min_df": min_df, "threshold": threshold},
        "counts": {"num_documents": len(abstracts)}
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(OUT_JSON)

def _pct(x: float) -> str:
    return f"{x*100:,.1f}%" if x is not None else "—"

def print_console_summary(json_path: Path):
    import json
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    seeds = data["seed_words_normalized"]
    agg = data["freq_total_seeds"]
    auto = data["auto_terms"]
    auto_agg = data["freq_total_auto"]
    eval_res = data["evaluation"]

    print("\n================ Requerimiento 3 — Resumen ================")
    print(f"Categoría: {data['category']}")
    print(f"Documentos (abstracts): {data['counts']['num_documents']}")
    print("-----------------------------------------------------------")
    print("Frecuencias globales (palabras asociadas provistas):")
    for s in seeds:
        print(f"  - {s:25s}  {agg.get(s, 0)}")
    print("-----------------------------------------------------------")
    print("Términos auto-generados (top) y frecuencias:")
    for t in auto:
        print(f"  - {t:25s}  {auto_agg.get(t, 0)}")
    print("-----------------------------------------------------------")
    print("Evaluación de precisión de nuevos términos (embeddings):")
    print(f"  Modelo: {eval_res['model']}  |  Umbral: {_pct(eval_res['threshold'])}")
    print(f"  Precisión: {_pct(eval_res['precision'])}")
    for d in eval_res["details"]:
        flag = "✔" if d["relevant"] else "✖"
        print(f"   {flag} {d['term']:25s}  sim={d['max_sim']:.3f}")
    print("===========================================================\n")

def main():
    ap = argparse.ArgumentParser(description="Requerimiento 3: Frecuencia de términos + auto términos + evaluación.")
    ap.add_argument("--bib", type=str, default=str(DEFAULT_BIB), help="Ruta al .bib (por defecto data/processed/productos_unificados.bib)")
    ap.add_argument("--max-terms", type=int, default=15, help="Máximo de términos auto-generados")
    ap.add_argument("--min-df", type=int, default=2, help="Mínimo documentos donde debe aparecer un término")
    ap.add_argument("--thr", type=float, default=0.50, help="Umbral de similitud (embeddings) para marcar relevancia")
    args = ap.parse_args()

    out = run_req3(bib_path=Path(args.bib), max_auto_terms=args.max_terms, min_df=args.min_df, threshold=args.thr)
    print(f"OK. Archivo generado: {out}")
    print_console_summary(Path(out))

if __name__ == "__main__":
    main()
