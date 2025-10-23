# requirement_4/run_req4.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List

from requirement_3.data_loader import load_bib_dataframe, DEFAULT_BIB  # carga abstracts desde .bib
from requirement_4.preprocess import preprocess_corpus
from requirement_4.similarity_matrix import build_similarity_matrix, similarity_to_distance
from requirement_4.clustering import run_hierarchical_clustering_pretty

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def _short_text(s: str, n: int = 52) -> str:
    """Trunca texto para etiquetas amigables en dendrograma."""
    s = (s or "").strip().replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"

def run_req4(
    bib_path: Path = DEFAULT_BIB,
    n_samples: int = 25,
    methods: List[str] | None = None,
    use_titles_as_labels: bool = True,
    color_threshold: float | None = None,
    leaf_font_size: int = 9,
) -> Dict[str, Any]:
    """
    Requerimiento 4:
      - Preprocesa abstracts
      - Calcula similitud (TF-IDF + coseno)
      - Convierte a distancia
      - Aplica clustering jerárquico (single/complete/average)
      - Genera dendrogramas estéticos en data/processed/

    Devuelve un dict con info básica (por si quieres inspeccionar en tests).
    """
    print("[RUN] Requerimiento 4 – Clustering jerárquico de abstracts")

    # 1) Cargar abstracts desde .bib
    df = load_bib_dataframe(bib_path)
    abstracts_all = [str(x) for x in df["abstract"].tolist() if isinstance(x, str)]
    titles_all    = [str(x) for x in df["title"].tolist()]

    # Submuestreo simple para visualización rápida
    if len(abstracts_all) > n_samples:
        abstracts = abstracts_all[:n_samples]
        titles    = titles_all[:n_samples]
        print(f"[INFO] Se tomarán {n_samples} abstracts para la demostración.")
    else:
        abstracts = abstracts_all
        titles    = titles_all

    # 2) Preprocesamiento
    corpus_clean = preprocess_corpus(abstracts)

    # 3) Similitud (TF-IDF + coseno) y distancia (1 - cos)
    sim = build_similarity_matrix(corpus_clean)
    dist = similarity_to_distance(sim)

    # 4) Etiquetas
    if use_titles_as_labels:
        labels = [f"A{i} — {_short_text(t)}" for i, t in enumerate(titles)]
        left_margin = 0.32  # deja margen extra para títulos
        max_label_len = 52
    else:
        labels = [f"A{i}" for i in range(len(abstracts))]
        left_margin = 0.22
        max_label_len = 42

    # 5) Métodos a comparar
    if methods is None:
        methods = ["single", "complete", "average"]

    results: Dict[str, Any] = {}
    for m in methods:
        out_file = OUT_DIR / f"dendrogram_{m}.png"
        print(f"[RUN] Dendrograma → método: {m}")
        info = run_hierarchical_clustering_pretty(
            distance_matrix=dist,
            labels=labels,
            method=m,
            title=f"Dendrograma — Método: {m}",
            out_file=str(out_file),
            color_threshold=color_threshold,   # None ⇒ 70% del máximo
            leaf_font_size=leaf_font_size,
            left_margin=left_margin,
            annotate_dist_axis=True,
            max_label_len=max_label_len,
        )
        results[m] = {
            "png": str(out_file),
            "color_threshold": info["color_threshold"],
            "leaf_order": info["order"],  # índices de hojas en el orden del gráfico
        }

    print("[OK] Dendrogramas generados en:", OUT_DIR)
    return results


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Requerimiento 4: Clustering jerárquico y dendrogramas estéticos.")
    ap.add_argument("--bib", type=str, default=str(DEFAULT_BIB), help="Ruta al archivo .bib")
    ap.add_argument("--n", type=int, default=25, help="Número de abstracts a agrupar (p.ej. 25)")
    ap.add_argument("--labels", choices=["titles", "ids"], default="titles", help="Etiquetas en hojas: títulos truncados o solo IDs")
    ap.add_argument("--thr", type=float, default=None, help="Umbral de color para clusters (None = 70% del máximo)")
    ap.add_argument("--font", type=int, default=9, help="Tamaño de fuente de las hojas")
    ap.add_argument("--methods", type=str, default="single,complete,average", help="Métodos separados por coma")

    args = ap.parse_args()
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    run_req4(
        bib_path=Path(args.bib),
        n_samples=args.n,
        methods=methods,
        use_titles_as_labels=(args.labels == "titles"),
        color_threshold=args.thr,
        leaf_font_size=args.font,
    )
