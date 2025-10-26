# requirement_grafos/run_grafos.py
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Any, Dict
from requirement_grafos.visualize import plot_citation_graph, plot_term_graph
# Núcleo de construcción de grafos
from requirement_grafos.cite_graph import build_citation_graph
from requirement_grafos.term_graph import build_term_graph
# Algoritmos de grafos
from requirement_grafos.algorithms import (
    dijkstra, reconstruct_path,
    floyd_warshall, fw_path,
    strongly_connected_components
)
# Visualización (PNG) del grafo de citaciones
from requirement_grafos.visualize import plot_citation_graph

# Rutas del proyecto
from requirement_3.data_loader import PROJECT_ROOT, DEFAULT_BIB

OUT_DIR = PROJECT_ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------- utilidades -------------------------
def save_json(obj: Dict[str, Any], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return str(path)


def console_summary_citations(
    g: Dict[str, Any],
    sample_src: str | None = None,
    sample_tgt: str | None = None,
    show_fw: bool = False
):
    """Resumen en consola para el grafo de citaciones (dirigido)."""
    nodes = g.get("nodes", [])
    edges = g.get("edges", [])
    adj = g.get("adj", {})

    print("\n==== Grafo de Citaciones (dirigido) ====")
    print(f"Nodos: {len(nodes)} | Aristas: {len(edges)}")

    # SCC (componentes fuertemente conexas)
    scc = strongly_connected_components(adj)
    scc_sorted = sorted(scc, key=len, reverse=True)
    tops = [len(c) for c in scc_sorted[:5]]
    print(f"Componentes fuertemente conexas (top 5 por tamaño): {tops}")

    # Camino mínimo (Dijkstra)
    if sample_src and sample_tgt and sample_src in adj and sample_tgt in adj:
        dist, prev = dijkstra(adj, sample_src)
        path = reconstruct_path(prev, sample_src, sample_tgt)
        if path:
            print(f"Camino mínimo (Dijkstra) {sample_src} → {sample_tgt}: {path}  costo={dist[sample_tgt]:.3f}")
        else:
            print(f"No hay camino (Dijkstra) entre {sample_src} y {sample_tgt}.")

    # (Opcional) Floyd–Warshall
    if show_fw and len(nodes) <= 160:  # evitar computación pesada en redes muy grandes
        print("Ejecutando Floyd–Warshall (todos contra todos)...")
        dist_fw, nxt_fw = floyd_warshall(adj)
        # Muestreo de 1 par si no se pasó explícito
        if not (sample_src and sample_tgt):
            if len(nodes) >= 2:
                sample_src = nodes[0]["id"]
                sample_tgt = nodes[min(1, len(nodes)-1)]["id"]
        if sample_src and sample_tgt:
            path_fw = fw_path(nxt_fw, sample_src, sample_tgt)
            if path_fw:
                print(f"Camino mínimo (FW) {sample_src} → {sample_tgt}: {path_fw}  costo={dist_fw[(sample_src, sample_tgt)]:.3f}")
            else:
                print(f"No hay camino (FW) entre {sample_src} y {sample_tgt}.")

    print("========================================\n")


def console_summary_terms(g: Dict[str, Any], top_k: int = 15):
    """Resumen en consola para el grafo de términos (no dirigido)."""
    nodes = g.get("nodes", [])
    edges = g.get("edges", [])
    degree = g.get("degree", {})
    comps = g.get("components", [])

    print("\n==== Grafo de Términos (no dirigido) ====")
    print(f"Nodos: {len(nodes)} | Aristas: {len(edges)}")
    # Top grados
    top = sorted(degree.items(), key=lambda x: -x[1])[:top_k]
    print("Términos con mayor grado:")
    for t, d in top:
        print(f"  - {t:25s} grado={d}")
    sizes = sorted([len(c) for c in comps], reverse=True)[:5]
    print(f"Componentes conexas (top 5 por tamaño): {sizes}")
    print("=========================================\n")


# --------------------- requerimiento: citaciones ---------------------
def run_req_grafos_citas(
    bib: Path = DEFAULT_BIB,
    min_sim: float = 0.35,
    plot: bool = True,
    max_nodes: int = 120,
    min_edge_sim: float = 0.40,
    show_fw: bool = False
) -> Dict[str, Any]:
    """
    Construye el grafo de citaciones dirigido e imprime métricas.
    - min_sim: umbral de similitud TF-IDF (título+keywords+autores) para inferir aristas
    - plot: si True, genera PNG del grafo
    - max_nodes: máximo de nodos a dibujar (top por grado) para legibilidad
    - min_edge_sim: umbral de similitud para dibujar aristas en la imagen
    """
    g = build_citation_graph(bib_path=bib, min_sim=min_sim, use_explicit=True)

    out_json = OUT_DIR / "grafos_citaciones.json"
    save_json(g, out_json)

    # Resumen consola
    sample_src = g["nodes"][0]["id"] if g.get("nodes") else None
    sample_tgt = g["nodes"][min(1, len(g.get('nodes', [])) - 1)]["id"] if g.get("nodes") else None
    console_summary_citations(g, sample_src=sample_src, sample_tgt=sample_tgt, show_fw=show_fw)

    # Imagen
    out_img = None
    if plot and g.get("nodes") and g.get("edges"):
        out_img_path = OUT_DIR / "grafos_citaciones.png"
        out_img = plot_citation_graph(
            g, out_img_path,
            max_nodes=max_nodes,
            min_edge_sim=min_edge_sim,
            with_labels=True
        )
        print(f"[OK] Imagen del grafo: {out_img}")

    return {"json": str(out_json), "png": out_img or ""}


# ---------------------- requerimiento: términos ----------------------
def run_req_grafos_terminos(
    bib: Path = DEFAULT_BIB,
    terms_path: Path | None = None,
    min_df: int = 3,
    window: int = 30,
    min_cooc: int = 2,
    top_k_print: int = 15,
    plot: bool = True,
    max_nodes: int = 150,
    min_edge_w: int = 2
) -> Dict[str, Any]:
    # cargar términos candidatos si se pasa archivo
    cand_terms: List[str] | None = None
    if terms_path and terms_path.exists():
        if terms_path.suffix.lower() == ".json":
            with open(terms_path, "r", encoding="utf-8") as f:
                cand_terms = json.load(f)
        else:
            cand_terms = [l.strip() for l in open(terms_path, "r", encoding="utf-8") if l.strip()]

    g = build_term_graph(
        bib_path=bib,
        candidate_terms=cand_terms,
        min_df=min_df,
        window=window,
        min_cooc=min_cooc
    )

    out_json = OUT_DIR / "grafos_terminos.json"
    save_json(g, out_json)
    console_summary_terms(g, top_k=top_k_print)

    out_img = None
    if plot and g.get("edges"):
        out_img_path = OUT_DIR / "grafos_terminos.png"
        out_img = plot_term_graph(
            g, out_img_path,
            max_nodes=max_nodes,
            min_edge_w=min_edge_w,
            with_labels=True
        )
        print(f"[OK] Imagen del grafo de términos: {out_img}")

    return {"json": str(out_json), "png": out_img or ""}

# ------------------------------ CLI ------------------------------
if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Grafos: citaciones (dirigido) y co-ocurrencia de términos (no dirigido)."
    )
    sub = ap.add_subparsers(dest="cmd")

    # Citaciones
    p1 = sub.add_parser("cit", help="Construir y analizar grafo de citaciones")
    p1.add_argument("--bib", type=str, default=str(DEFAULT_BIB), help="Ruta al .bib")
    p1.add_argument("--min-sim", type=float, default=0.35, help="Umbral de similitud para inferir aristas")
    p1.add_argument("--plot", action="store_true", help="Generar imagen PNG del grafo")
    p1.add_argument("--max-nodes", type=int, default=120, help="Máximo de nodos a dibujar (top por grado)")
    p1.add_argument("--emin", type=float, default=0.40, help="Similitud mínima para dibujar aristas")
    p1.add_argument("--fw", action="store_true", help="(Opcional) Ejecutar también Floyd–Warshall (redes pequeñas)")

    # Términos
    p2 = sub.add_parser("terms", help="Construir y analizar grafo de términos")
    p2.add_argument("--bib", type=str, default=str(DEFAULT_BIB), help="Ruta al .bib")
    p2.add_argument("--terms", type=str, default="", help="Ruta a JSON/TXT con términos (opcional)")
    p2.add_argument("--min-df", type=int, default=3, help="Mínimo DF para incluir términos si no se pasan candidatos")
    p2.add_argument("--window", type=int, default=30, help="Tamaño de ventana de co-ocurrencia")
    p2.add_argument("--min-cooc", type=int, default=2, help="Co-ocurrencias mínimas para crear arista")
    p2.add_argument("--plot", action="store_true", help="Generar imagen PNG del grafo de términos")
    p2.add_argument("--max-nodes", type=int, default=150, help="Máximo de nodos a dibujar (top por grado)")
    p2.add_argument("--emin", type=int, default=2, help="Peso mínimo (co-ocurrencia) para dibujar aristas")

    args = ap.parse_args()

    if args.cmd == "cit":
        run_req_grafos_citas(
            bib=Path(args.bib),
            min_sim=args.min_sim,
            plot=args.plot,
            max_nodes=args.max_nodes,
            min_edge_sim=args.emin,
            show_fw=args.fw
        )

    elif args.cmd == "terms":
        terms = Path(args.terms) if args.terms else None
        run_req_grafos_terminos(
            bib=Path(args.bib),
            terms_path=terms,
            min_df=args.min_df,
            window=args.window,
            min_cooc=args.min_cooc,
            plot=args.plot,
            max_nodes=args.max_nodes,
            min_edge_w=args.emin
        )

    else:
        ap.print_help()
