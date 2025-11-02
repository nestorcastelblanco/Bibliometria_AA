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

OUT_DIR = PROJECT_ROOT / "requirement_grafos"
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
    show_fw: bool = True
):
    """Resumen en consola para el grafo de citaciones (dirigido)."""
    nodes = g.get("nodes", [])
    edges = g.get("edges", [])
    adj = g.get("adj", {})

    print("\n" + "="*70)
    print("  REPORTE: GRAFO DE CITACIONES (DIRIGIDO)")
    print("="*70)
    
    # 1. Estructura básica del grafo
    print("\n[1] ESTRUCTURA DEL GRAFO")
    print(f"  • Nodos (artículos): {len(nodes)}")
    print(f"  • Aristas (citaciones): {len(edges)}")
    if edges:
        weights = [e['w'] for e in edges]
        print(f"  • Peso mínimo de arista: {min(weights):.4f}")
        print(f"  • Peso máximo de arista: {max(weights):.4f}")
        print(f"  • Peso promedio: {sum(weights)/len(weights):.4f}")
    
    # Grado de nodos (entrada y salida)
    in_degree = {n['id']: 0 for n in nodes}
    out_degree = {n['id']: 0 for n in nodes}
    for e in edges:
        out_degree[e['u']] += 1
        in_degree[e['v']] += 1
    
    max_in = max(in_degree.items(), key=lambda x: x[1])
    max_out = max(out_degree.items(), key=lambda x: x[1])
    
    print(f"\n  • Nodo más citado (grado entrada): {max_in[0]} con {max_in[1]} citas")
    node_data = next(n for n in nodes if n['id'] == max_in[0])
    print(f"    Título: {node_data['title'][:60]}...")
    
    print(f"  • Nodo que más cita (grado salida): {max_out[0]} con {max_out[1]} citas")
    node_data = next(n for n in nodes if n['id'] == max_out[0])
    print(f"    Título: {node_data['title'][:60]}...")

    # 2. Componentes fuertemente conexas (SCC)
    print("\n[2] COMPONENTES FUERTEMENTE CONEXAS (Algoritmo de Kosaraju)")
    scc = strongly_connected_components(adj)
    scc_sorted = sorted(scc, key=len, reverse=True)
    print(f"  • Total de componentes: {len(scc_sorted)}")
    print(f"  • Tamaños (top 10): {[len(c) for c in scc_sorted[:10]]}")
    
    if scc_sorted[0] and len(scc_sorted[0]) > 1:
        print(f"  • Componente más grande tiene {len(scc_sorted[0])} nodos:")
        print(f"    Nodos: {scc_sorted[0][:10]}{'...' if len(scc_sorted[0]) > 10 else ''}")
    else:
        print(f"  • No hay ciclos de citación (todas las componentes son de tamaño 1)")

    # 3. Caminos mínimos (Dijkstra)
    print("\n[3] CAMINOS MÍNIMOS (Algoritmo de Dijkstra)")
    
    # Buscar pares conectados para demostrar
    connected_pairs = []
    for e in edges[:50]:  # Revisar primeras 50 aristas
        u, v = e['u'], e['v']
        dist, prev = dijkstra(adj, u)
        if dist[v] < float('inf'):
            connected_pairs.append((u, v, dist[v]))
        if len(connected_pairs) >= 3:
            break
    
    if connected_pairs:
        for u, v, cost in connected_pairs[:3]:
            dist, prev = dijkstra(adj, u)
            path = reconstruct_path(prev, u, v)
            node_u = next(n for n in nodes if n['id'] == u)
            node_v = next(n for n in nodes if n['id'] == v)
            print(f"  • Camino: {u} → {v}")
            print(f"    Origen: {node_u['title'][:50]}...")
            print(f"    Destino: {node_v['title'][:50]}...")
            print(f"    Ruta: {' → '.join(path)}")
            print(f"    Costo total: {cost:.4f}")
    else:
        print(f"  • No se encontraron caminos conectados (grafo muy disperso)")
        if sample_src and sample_tgt and sample_src in adj and sample_tgt in adj:
            dist, prev = dijkstra(adj, sample_src)
            path = reconstruct_path(prev, sample_src, sample_tgt)
            if path:
                print(f"  • Camino {sample_src} → {sample_tgt}: {path}  costo={dist[sample_tgt]:.3f}")
            else:
                print(f"  • No hay camino entre {sample_src} y {sample_tgt}")

    # 4. Floyd-Warshall (opcional, solo para grafos pequeños)
    if show_fw and len(nodes) <= 150:
        print("\n[4] ANÁLISIS COMPLETO (Algoritmo de Floyd-Warshall)")
        print(f"  • Ejecutando análisis de todos los pares de nodos...")
        dist_fw, nxt_fw = floyd_warshall(adj)
        
        # Contar pares conectados
        connected = sum(1 for (i,j) in dist_fw if i != j and dist_fw[(i,j)] < float('inf'))
        total_pairs = len(nodes) * (len(nodes) - 1)
        print(f"  • Pares conectados: {connected} de {total_pairs} ({100*connected/total_pairs:.2f}%)")
        
        # Encontrar camino más largo
        max_dist = max(d for (i,j), d in dist_fw.items() if i != j and d < float('inf'))
        max_pair = [k for k, d in dist_fw.items() if d == max_dist][0]
        path_longest = fw_path(nxt_fw, max_pair[0], max_pair[1])
        print(f"  • Camino más largo: {max_pair[0]} → {max_pair[1]}")
        print(f"    Longitud: {len(path_longest)-1} saltos, costo: {max_dist:.4f}")
    elif show_fw:
        print("\n[4] Floyd-Warshall: Omitido (grafo muy grande, >150 nodos)")

    print("\n" + "="*70 + "\n")


def console_summary_terms(g: Dict[str, Any], top_k: int = 20):
    """Resumen en consola para el grafo de términos (no dirigido)."""
    nodes = g.get("nodes", [])
    edges = g.get("edges", [])
    degree = g.get("degree", {})
    comps = g.get("components", [])

    print("\n" + "="*70)
    print("  REPORTE: GRAFO DE CO-OCURRENCIA DE TÉRMINOS (NO DIRIGIDO)")
    print("="*70)
    
    # 1. Estructura básica del grafo
    print("\n[1] CONSTRUCCIÓN DEL GRAFO DE CO-OCURRENCIA")
    print(f"  • Nodos (términos únicos): {len(nodes)}")
    print(f"  • Aristas (co-ocurrencias): {len(edges)}")
    
    if edges:
        weights = [e['w'] for e in edges]
        print(f"  • Co-ocurrencia mínima: {min(weights)} veces")
        print(f"  • Co-ocurrencia máxima: {max(weights)} veces")
        print(f"  • Co-ocurrencia promedio: {sum(weights)/len(weights):.2f} veces")
        print(f"  • Densidad del grafo: {2*len(edges)/(len(nodes)*(len(nodes)-1))*100:.4f}%")
    
    # 2. Grado de los nodos (términos más conectados)
    print(f"\n[2] GRADO DE NODOS - TÉRMINOS MÁS RELACIONADOS")
    
    # Recalcular grados desde las aristas para tener datos correctos
    recalc_degree = {}
    for e in edges:
        u, v = e['u'], e['v']
        recalc_degree[u] = recalc_degree.get(u, 0) + 1
        recalc_degree[v] = recalc_degree.get(v, 0) + 1
    
    # Filtrar términos problemáticos ANTES de ordenar
    valid_degrees = {t: d for t, d in recalc_degree.items() if len(t) > 2 and t not in ['u', 'v']}
    
    if not valid_degrees:
        print("  ⚠️  No se encontraron términos válidos con conexiones")
    else:
        print(f"  Términos con mayor número de conexiones (top {top_k}):\n")
        
        top = sorted(valid_degrees.items(), key=lambda x: -x[1])[:top_k]
        
        print("  Término                     Grado (conexiones)  % del total")
        print("  " + "-"*60)
        max_degree = top[0][1] if top else 1
        for i, (term, deg) in enumerate(top, 1):
            pct = (deg / len(edges)) * 100 if edges else 0
            bar_len = int(30 * deg / max_degree) if max_degree > 0 else 0
            bar = "█" * bar_len
            print(f"  {i:2d}. {term:25s} {deg:6d}  ({pct:5.2f}%) {bar}")
    
    # Mostrar términos problemáticos si existen
    problematic = [(t, d) for t, d in recalc_degree.items() if t in ['u', 'v'] or (len(t) <= 2 and d > 1000)]
    if problematic:
        print(f"\n  ⚠️  Términos genéricos detectados (artefactos del procesamiento):")
        for t, d in problematic[:5]:
            print(f"      '{t}' con grado {d} - posible error de tokenización")
    
    # Estadísticas de grado
    degrees = list(degree.values())
    if degrees:
        print(f"\n  Estadísticas de grado:")
        print(f"  • Grado mínimo: {min(degrees)}")
        print(f"  • Grado máximo: {max(degrees)}")
        print(f"  • Grado promedio: {sum(degrees)/len(degrees):.2f}")
        print(f"  • Grado mediano: {sorted(degrees)[len(degrees)//2]}")

    # 3. Componentes conexas (detección de grupos temáticos)
    print(f"\n[3] COMPONENTES CONEXAS - GRUPOS DE TÉRMINOS RELACIONADOS")
    print(f"  Algoritmo: Búsqueda en profundidad (DFS)")
    print(f"  • Total de componentes: {len(comps)}")
    
    sizes = sorted([len(c) for c in comps], reverse=True)
    print(f"  • Tamaños (top 10): {sizes[:10]}")
    
    if comps and len(comps[0]) == len(nodes):
        print(f"\n  ✓ Todos los términos están interconectados (1 componente gigante)")
        print(f"    Esto indica una alta cohesión temática en el corpus")
    elif comps:
        print(f"\n  • Componente más grande: {len(comps[0])} términos ({len(comps[0])/len(nodes)*100:.1f}% del total)")
        if len(comps[0]) <= 30:
            print(f"    Términos: {', '.join(comps[0][:20])}{'...' if len(comps[0]) > 20 else ''}")
        
        if len(comps) > 1 and len(comps[1]) > 1:
            print(f"  • Segunda componente: {len(comps[1])} términos")
            if len(comps[1]) <= 20:
                print(f"    Términos: {', '.join(comps[1][:15])}{'...' if len(comps[1]) > 15 else ''}")
        
        # Componentes aisladas (temas específicos)
        isolated = [c for c in comps if len(c) == 1]
        if isolated:
            print(f"  • Términos aislados (sin co-ocurrencias): {len(isolated)}")
            if len(isolated) <= 10:
                print(f"    Ejemplos: {', '.join([c[0] for c in isolated[:10]])}")
    
    # 4. Análisis de aristas (co-ocurrencias más fuertes)
    if edges:
        print(f"\n[4] CO-OCURRENCIAS MÁS FUERTES")
        top_edges = sorted(edges, key=lambda e: e['w'], reverse=True)[:10]
        print(f"  Top 10 pares de términos que co-ocurren más frecuentemente:\n")
        print("  Término 1                 Término 2                 Co-ocurrencias")
        print("  " + "-"*68)
        for i, e in enumerate(top_edges, 1):
            t1, t2, w = e['u'], e['v'], e['w']
            print(f"  {i:2d}. {t1:25s} ↔ {t2:25s} {w:4d} veces")
    
    print("\n" + "="*70 + "\n")


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
