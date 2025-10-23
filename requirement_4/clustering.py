from __future__ import annotations
from typing import List, Optional, Dict, Any, Callable
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram

# Paleta de colores agradable (sin depender de seaborn)
PALETTE = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
    "#06B6D4", "#6366F1", "#84CC16", "#F97316", "#EC4899"
]

def _truncate(s: str, n: int = 42) -> str:
    s = (s or "").strip().replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"

def _make_link_color_func(thr: float) -> Callable[[float], str]:
    """Colorea los enlaces por debajo del umbral con colores de la paleta."""
    def f(k):
        # k es la distancia del enlace. SciPy pasa k como 'c' para link_color_func.
        # Si k <= thr -> usar color de cluster, si no -> gris claro.
        return None  # devolvemos None para permitir la lógica de color_threshold de scipy
    return f

def _apply_matplotlib_style():
    plt.rcParams.update({
        "figure.figsize": (14, 8),
        "axes.titlesize": 18,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "grid.color": "#E5E7EB",
        "grid.linestyle": "-",
        "grid.linewidth": 0.8,
        "axes.grid": False,
        "lines.linewidth": 1.6,
    })

def run_hierarchical_clustering_pretty(
    distance_matrix: np.ndarray,
    labels: Optional[List[str]] = None,
    method: str = "average",
    title: Optional[str] = None,
    out_file: Optional[str] = None,
    color_threshold: Optional[float] = None,
    leaf_font_size: int = 9,
    left_margin: float = 0.25,   # margen para etiquetas largas
    annotate_dist_axis: bool = True,
    max_label_len: int = 42,
) -> Dict[str, Any]:
    """
    Genera un dendrograma estético y legible (horizontal) para clustering jerárquico.

    distance_matrix : matriz cuadrada de distancias en [0,1]
    labels          : etiquetas de hojas (se truncarán para legibilidad)
    method          : 'single' | 'complete' | 'average' | 'ward'...
    color_threshold : umbral para colorear clusters (si None, usa 70% del máximo)
    out_file        : ruta a PNG/SVG. Si None, muestra en pantalla.
    """

    _apply_matplotlib_style()

    # SciPy espera un vector "condensed" (triángulo superior sin diagonal)
    condensed = distance_matrix[np.triu_indices_from(distance_matrix, k=1)]
    Z = linkage(condensed, method=method)

    # Umbral de color por defecto (70% del máximo)
    if color_threshold is None:
        color_threshold = float(np.max(Z[:, 2]) * 0.7)

    # Preparar etiquetas truncadas
    if labels:
        lab = [_truncate(x, max_label_len) for x in labels]
    else:
        lab = None

    fig, ax = plt.subplots(figsize=(14, 8))
    # Dendrograma horizontal (right) con colores de clusters
    dkwargs = dict(
        orientation="right",
        labels=lab,
        leaf_font_size=leaf_font_size,
        above_threshold_color="#94A3B8",  # gris p/ ramas por encima del umbral
        color_threshold=color_threshold,
    )
    D = dendrogram(Z, **dkwargs)

    # Colorear las ramas por debajo del umbral con paleta (scipy ya colorea grupos distintos;
    # opcionalmente podríamos re-mapear colores recorriendo LineCollections de ax)
    # Ajustes de ejes y estilo
    ax.set_title(title or f"Dendrograma — Método: {method}")
    ax.set_xlabel("Distancia (1 − similitud)")
    ax.set_ylabel("Abstracts")
    ax.tick_params(axis="x", which="both", length=0)
    ax.tick_params(axis="y", which="both", length=0)

    # Cuadrícula vertical suave para facilitar lectura de distancias
    if annotate_dist_axis:
        ax.xaxis.grid(True)

    # Márgenes y tight layout
    plt.subplots_adjust(left=left_margin, right=0.98, top=0.92, bottom=0.08)

    if out_file:
        # Guardar en alta resolución y también como SVG (vectorial) si se pide .svg
        ext = out_file.split(".")[-1].lower()
        dpi = 240 if ext in ("png", "jpg", "jpeg") else 96
        plt.savefig(out_file, dpi=dpi, bbox_inches="tight")
        print(f"[OK] Dendrograma guardado en {out_file}")
        plt.close(fig)
    else:
        plt.show()

    return {"Z": Z, "color_threshold": color_threshold, "order": D.get("leaves", [])}
