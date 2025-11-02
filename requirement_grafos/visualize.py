# requirement_grafos/visualize.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Tuple
import math
import matplotlib.pyplot as plt
from matplotlib import cm

# networkx es opcional (layout más bonito)
try:
    import networkx as nx
    _HAS_NX = True
except Exception:
    _HAS_NX = False


def _truncate(s: str, n: int = 30) -> str:
    """Trunca el texto a n caracteres, reemplazando saltos de línea por espacios."""
    s = (s or "").strip().replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


# ------------------ CITATION GRAPH (dirigido) ------------------ #
def _pick_top_nodes(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], max_nodes: int) -> List[str]:
    deg = {n["id"]: 0 for n in nodes}
    for e in edges:
        deg[e["u"]] = deg.get(e["u"], 0) + 1
        deg[e["v"]] = deg.get(e["v"], 0) + 1
    ranked = sorted(deg.items(), key=lambda x: -x[1])
    keep = [u for u, _ in ranked[:max_nodes]]
    return keep

def _colors_by_component(adj: Dict[str, Dict[str, float]], nodes_keep: List[str]) -> Dict[str, Tuple[float,float,float,float]]:
    # Kosaraju sobre subgrafo (para citaciones)
    sg = {u: {v:w for v, w in adj.get(u, {}).items() if v in nodes_keep} for u in nodes_keep}
    sys_nodes = list(sg.keys())
    tr = {u:{} for u in sys_nodes}
    for u in sg:
        for v in sg[u]:
            tr.setdefault(v, {})
            tr[v][u] = sg[u][v]
    visited = set(); order: List[str] = []
    def dfs1(u: str):
        visited.add(u)
        for v in sg[u]:
            if v not in visited: dfs1(v)
        order.append(u)
    for u in sys_nodes:
        if u not in visited: dfs1(u)
    visited.clear()
    comps: List[List[str]] = []
    def dfs2(u: str, comp: List[str]):
        visited.add(u); comp.append(u)
        for v in tr[u]:
            if v not in visited: dfs2(v, comp)
    for u in reversed(order):
        if u not in visited:
            comp: List[str] = []
            dfs2(u, comp); comps.append(comp)
    palette = cm.get_cmap("tab20", max(2, len(comps)))
    colors: Dict[str, Tuple[float,float,float,float]] = {}
    for i, comp in enumerate(comps):
        col = palette(i)
        for u in comp:
            colors[u] = col
    return colors

def plot_citation_graph(
    g: Dict[str, Any],
    out_png: Path,
    *,
    max_nodes: int = 120,
    min_edge_sim: float = 0.40,
    with_labels: bool = True,
    seed: int = 42,
    dpi: int = 240,
) -> str:
    nodes = g["nodes"]; edges = g["edges"]; adj = g["adj"]
    fedges = [e for e in edges if float(e.get("w", 0.0)) >= min_edge_sim]
    if not fedges:
        raise ValueError("No hay aristas luego del umbral. Baja 'min_edge_sim'.")
    keep = _pick_top_nodes(nodes, fedges, max_nodes=max_nodes)
    keep_set = set(keep)
    fedges = [e for e in fedges if e["u"] in keep_set and e["v"] in keep_set]
    fnodes = [n for n in nodes if n["id"] in keep_set]
    node_colors = _colors_by_component(adj, keep)
    deg = {n["id"]: 0 for n in fnodes}
    for e in fedges:
        deg[e["u"]] += 1; deg[e["v"]] += 1
    sizes = {u: 200 + 60*math.sqrt(max(1, d)) for u, d in deg.items()}
    if _HAS_NX:
        DG = nx.DiGraph()
        DG.add_nodes_from([n["id"] for n in fnodes])
        for e in fedges:
            DG.add_edge(e["u"], e["v"], weight=float(e["w"]))
        # Usar spring_layout con más iteraciones y mayor separación (k)
        pos = nx.spring_layout(DG, k=2.5, iterations=100, seed=seed, scale=2.0)
    else:
        import numpy as np
        ids = [n["id"] for n in fnodes]
        theta = np.linspace(0, 2*np.pi, len(ids), endpoint=False)
        # Aumentar el radio del círculo para mayor separación
        pos = {u: (2.0*float(math.cos(t)), 2.0*float(math.sin(t))) for u, t in zip(ids, theta)}
    plt.figure(figsize=(28, 22)); ax = plt.gca()
    ax.set_title("Grafo de Citaciones (dirigido)", fontsize=18, fontweight="bold", pad=20)
    
    # Dibujar aristas
    for e in fedges:
        u, v, w = e["u"], e["v"], float(e["w"])
        x1, y1 = pos[u]; x2, y2 = pos[v]
        lw = 0.5 + 2.5*(w - min_edge_sim)/(1.0 - min_edge_sim + 1e-6)
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=lw, alpha=0.3, color="#94A3B8"))
    
    # Dibujar nodos
    for n in fnodes:
        u = n["id"]; x, y = pos[u]
        col = node_colors.get(u, (0.3, 0.5, 0.8, 1.0))
        sz = sizes.get(u, 250)
        ax.scatter([x], [y], s=sz, c=[col], edgecolors="white", linewidths=1.2, zorder=3, alpha=0.9)
    
    # Dibujar etiquetas con fondo blanco semitransparente para legibilidad
    if with_labels:
        for n in fnodes:
            u = n["id"]; ttl = _truncate(n.get("title", ""), 35); x, y = pos[u]
            ax.text(x, y, f"{u}: {ttl}", fontsize=8, ha="center", va="center", 
                    color="black", weight="normal",
                    bbox=dict(boxstyle="round,pad=0.35", facecolor="white", 
                             edgecolor="gray", linewidth=0.3, alpha=0.85))
    
    ax.axis("off"); plt.tight_layout(); out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=dpi, bbox_inches="tight"); plt.close()
    return str(out_png)


# ------------------ TERM GRAPH (no dirigido) ------------------ #
def plot_term_graph(
    g: Dict[str, Any],
    out_png: Path,
    *,
    max_nodes: int = 150,      # límite para legibilidad
    min_edge_w: int = 2,       # co-ocurrencia mínima para dibujar
    with_labels: bool = True,
    seed: int = 42,
    dpi: int = 240,
) -> str:
    """
    Dibuja el grafo de co-ocurrencia de términos (no dirigido).
      - tamaño de nodo: ~ grado
      - grosor de arista: ~ co-ocurrencia
      - color de nodo: por componente conexa
    """
    nodes = g.get("nodes", [])
    edges = g.get("edges", [])
    degree = g.get("degree", {})
    comps = g.get("components", [])
    if not nodes or not edges:
        raise ValueError("El grafo no tiene nodos o aristas para dibujar.")

    # filtrar aristas por peso y escoger top nodos por grado
    fedges = [e for e in edges if int(e.get("w", 0)) >= int(min_edge_w)]
    if not fedges:
        raise ValueError("No hay aristas tras aplicar 'min_edge_w'. Baja el umbral.")
    # top por grado
    ranked = sorted(degree.items(), key=lambda x: -x[1])[:max_nodes]
    keep = {u for u, _ in ranked}
    fedges = [e for e in fedges if e["u"] in keep and e["v"] in keep]
    fnodes = [n for n in nodes if n["id"] in keep]

    # colores por componente conexa
    # mapear id->comp
    comp_index: Dict[str, int] = {}
    for i, comp in enumerate(comps):
        for u in comp:
            comp_index[u] = i
    palette = cm.get_cmap("tab20", max(2, len(comps)))
    node_colors = {n["id"]: palette(comp_index.get(n["id"], 0)) for n in fnodes}

    # tamaños por grado (con límite superior para evitar nodos demasiado grandes)
    # Aumentar tamaño base y factor para mejor visibilidad
    raw_sizes = {u: 500 + 150*math.sqrt(max(1, degree.get(u, 1))) for u in keep}
    max_size = 4500  # Límite superior para nodos muy conectados
    sizes = {u: min(s, max_size) for u, s in raw_sizes.items()}

    # construir graph para layout
    if _HAS_NX:
        UG = nx.Graph()
        UG.add_nodes_from([n["id"] for n in fnodes])
        for e in fedges:
            UG.add_edge(e["u"], e["v"], weight=float(e["w"]))
        # Layout con mucha más separación y más iteraciones
        pos = nx.spring_layout(UG, k=3.0, iterations=150, seed=seed, scale=2.5)
    else:
        # círculo fallback con mayor radio
        import numpy as np
        ids = [n["id"] for n in fnodes]
        theta = np.linspace(0, 2*np.pi, len(ids), endpoint=False)
        pos = {u: (2.5*float(math.cos(t)), 2.5*float(math.sin(t))) for u, t in zip(ids, theta)}

    # dibujar - figura más grande
    plt.figure(figsize=(30, 24)); ax = plt.gca()
    ax.set_title("Grafo de Co-ocurrencia de Términos (no dirigido)", fontsize=20, fontweight="bold", pad=20)

    # aristas con grosor según co-ocurrencia (más visibles)
    wmin = min(int(e["w"]) for e in fedges)
    wmax = max(int(e["w"]) for e in fedges)
    for e in fedges:
        u, v, w = e["u"], e["v"], int(e["w"])
        x1, y1 = pos[u]; x2, y2 = pos[v]
        # normalizar grosor
        lw = 0.4 + 1.8 * ((w - wmin) / (max(1, wmax - wmin)))
        ax.plot([x1, x2], [y1, y2], color="#94A3B8", lw=lw, alpha=0.45, zorder=1)

    # nodos con mejor contraste
    for n in fnodes:
        u = n["id"]; x, y = pos[u]
        col = node_colors.get(u, (0.3, 0.5, 0.8, 1.0))
        sz = sizes.get(u, 220)
        ax.scatter([x], [y], s=sz, c=[col], edgecolors="white", linewidths=1.2, zorder=2, alpha=0.9)

    # etiquetas con fondo blanco para legibilidad
    if with_labels:
        for n in fnodes:
            u = n["id"]; x, y = pos[u]
            ax.text(x, y, _truncate(u, 25), fontsize=9, ha="center", va="center", 
                    color="black", weight="medium", zorder=3,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="white", 
                             edgecolor="gray", linewidth=0.3, alpha=0.88))

    ax.axis("off"); plt.tight_layout(); out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=dpi, bbox_inches="tight"); plt.close()
    return str(out_png)
