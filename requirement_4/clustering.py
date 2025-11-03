"""
Módulo de clustering jerárquico y generación de dendrogramas estéticos.

Implementa clustering aglomerativo con múltiples métodos de enlace
(single, complete, average, ward) y genera visualizaciones de alta calidad.

Parte del Requerimiento 4: Clustering jerárquico y dendrogramas.
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any, Callable
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram

# Paleta de colores moderna para clusters (inspirada en Tailwind CSS)
PALETTE = [
    "#3B82F6",  # Blue
    "#10B981",  # Green
    "#F59E0B",  # Amber
    "#EF4444",  # Red
    "#8B5CF6",  # Violet
    "#06B6D4",  # Cyan
    "#6366F1",  # Indigo
    "#84CC16",  # Lime
    "#F97316",  # Orange
    "#EC4899"   # Pink
]

def _truncate(s: str, n: int = 42) -> str:
    """
    Trunca string a longitud máxima para etiquetas de dendrograma.
    
    Args:
        s (str): String a truncar
        n (int, optional): Longitud máxima. Default: 42
    
    Returns:
        str: String truncado con '…' si excede longitud
    
    Example:
        >>> _truncate("Machine Learning for Data Science Applications", 30)
        'Machine Learning for Data S…'
        >>> _truncate("Short", 30)
        'Short'
    
    Notas:
        - Elimina saltos de línea y espacios extra
        - Usa carácter Unicode '…' (ellipsis) para indicar truncamiento
        - Útil para mantener dendrogramas legibles con etiquetas largas
    """
    s = (s or "").strip().replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"

def _make_link_color_func(thr: float) -> Callable[[float], str]:
    """
    Crea función de color para enlaces del dendrograma según umbral.
    
    Args:
        thr (float): Umbral de distancia para separar clusters
    
    Returns:
        Callable: Función que mapea distancia k a color
    
    Notas:
        - Actualmente retorna None para usar lógica default de scipy
        - scipy.cluster.hierarchy.dendrogram maneja colores automáticamente
        - color_threshold parámetro principal colorea clusters < umbral
        - Enlaces > umbral usan above_threshold_color (gris)
        - Reservado para extensiones futuras con paleta personalizada
    """
    def f(k):
        # k es la distancia del enlace. SciPy pasa k como 'c' para link_color_func.
        # Si k <= thr → usar color de cluster, si no → gris claro.
        return None  # devolvemos None para permitir la lógica de color_threshold de scipy
    return f

def _apply_matplotlib_style():
    """
    Aplica estilo visual consistente a figuras de matplotlib.
    
    Configura parámetros globales de matplotlib para dendrogramas profesionales:
    - Tamaño de figura: 14x8"
    - Fondo blanco limpio
    - Fuentes: título 18pt bold, labels 12pt, ticks 10pt
    - Grid sutil (#E5E7EB) desactivado por default
    - Líneas medias (1.6pt)
    
    Returns:
        None: Modifica plt.rcParams globalmente
    
    Notas:
        - Se llama antes de generar cada dendrograma
        - Estilo minimalista para publicaciones científicas
        - Grid se activa selectivamente con ax.xaxis.grid(True)
        - Colores inspirados en Tailwind CSS (paleta moderna)
    """
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
    Genera dendrograma estético y legible (horizontal) para clustering jerárquico.
    
    Proceso de 6 pasos:
    1. Configura estilo visual matplotlib
    2. Convierte matriz de distancia a formato condensado (scipy)
    3. Ejecuta clustering jerárquico con método de enlace especificado
    4. Genera dendrograma con colores por cluster
    5. Aplica estilos y anotaciones
    6. Guarda PNG/SVG de alta resolución
    
    Args:
        distance_matrix (np.ndarray): Matriz NxN de distancias en [0,1]
        labels (List[str] | None, optional): Etiquetas de hojas (se truncan automáticamente)
        method (str, optional): Método de enlace. Options: 'single', 'complete', 'average', 'ward'.
            Default: 'average'
        title (str | None, optional): Título del gráfico. Default: auto-generado
        out_file (str | None, optional): Ruta de salida PNG/SVG. None → muestra en pantalla
        color_threshold (float | None, optional): Umbral de distancia para colorear clusters.
            None → usa 70% del máximo. Default: None
        leaf_font_size (int, optional): Tamaño de fuente de etiquetas. Default: 9
        left_margin (float, optional): Margen izquierdo para etiquetas largas. Default: 0.25
        annotate_dist_axis (bool, optional): Mostrar grid en eje X (distancias). Default: True
        max_label_len (int, optional): Longitud máxima de etiquetas antes de truncar. Default: 42
    
    Returns:
        dict: Información del clustering con keys:
            - Z: Matriz de enlace (linkage matrix) de scipy
            - color_threshold: Umbral usado para colorear
            - order: Lista de índices de hojas en orden del dendrograma
    
    Métodos de enlace:
        - 'single': Distancia mínima (sensible a cadenas)
        - 'complete': Distancia máxima (clusters compactos)
        - 'average': Distancia promedio (balanceado, recomendado)
        - 'ward': Minimiza varianza intra-cluster (requiere distancias euclidianas)
    
    Example:
        >>> dist = np.array([[0, 0.3, 0.8], [0.3, 0, 0.9], [0.8, 0.9, 0]])
        >>> labels = ["Doc1", "Doc2", "Doc3"]
        >>> result = run_hierarchical_clustering_pretty(
        ...     distance_matrix=dist,
        ...     labels=labels,
        ...     method="average",
        ...     out_file="dendrogram.png"
        ... )
        >>> result.keys()
        dict_keys(['Z', 'color_threshold', 'order'])
    
    Características visuales:
        - Orientación horizontal (right) para mejor legibilidad
        - Colores automáticos por cluster (< color_threshold)
        - Ramas superiores en gris (#94A3B8)
        - Grid vertical sutil para lectura de distancias
        - Alta resolución: DPI 240 para PNG
        - Soporte SVG vectorial
    
    Notas:
        - distance_matrix debe ser simétrica con diagonal = 0
        - scipy requiere formato condensado (triángulo superior sin diagonal)
        - color_threshold = 0.7 * max(Z[:,2]) es regla empírica efectiva
        - Etiquetas largas se truncan automáticamente con '…'
        - left_margin debe aumentarse para etiquetas más largas
    """

    # PASO 1: Aplicar estilo visual consistente
    _apply_matplotlib_style()

    # PASO 2: Convertir matriz a formato condensado para scipy
    # SciPy espera un vector "condensed" (triángulo superior sin diagonal)
    condensed = distance_matrix[np.triu_indices_from(distance_matrix, k=1)]
    
    # PASO 3: Ejecutar clustering jerárquico
    Z = linkage(condensed, method=method)

    # Umbral de color por defecto (70% del máximo)
    if color_threshold is None:
        color_threshold = float(np.max(Z[:, 2]) * 0.7)

    # Preparar etiquetas truncadas
    if labels:
        lab = [_truncate(x, max_label_len) for x in labels]
    else:
        lab = None

    # PASO 4: Generar dendrograma horizontal con colores
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Configuración de dendrograma horizontal (right)
    dkwargs = dict(
        orientation="right",  # Horizontal: etiquetas a la derecha
        labels=lab,
        leaf_font_size=leaf_font_size,
        above_threshold_color="#94A3B8",  # Gris para ramas > umbral
        color_threshold=color_threshold,  # Colorea clusters < umbral
    )
    D = dendrogram(Z, **dkwargs)

    # PASO 5: Aplicar estilos y anotaciones
    # scipy colorea automáticamente grupos distintos con paleta default
    # (opcionalmente podríamos re-mapear colores usando PALETTE)
    
    # Títulos y etiquetas de ejes
    ax.set_title(title or f"Dendrograma — Método: {method}")
    ax.set_xlabel("Distancia (1 − similitud)")
    ax.set_ylabel("Abstracts")
    
    # Eliminar ticks para estética limpia
    ax.tick_params(axis="x", which="both", length=0)
    ax.tick_params(axis="y", which="both", length=0)

    # Cuadrícula vertical suave para facilitar lectura de distancias
    if annotate_dist_axis:
        ax.xaxis.grid(True)

    # Márgenes personalizados (espacio para etiquetas largas)
    plt.subplots_adjust(left=left_margin, right=0.98, top=0.92, bottom=0.08)

    # PASO 6: Guardar o mostrar
    if out_file:
        # Alta resolución para publicaciones
        ext = out_file.split(".")[-1].lower()
        dpi = 240 if ext in ("png", "jpg", "jpeg") else 96
        plt.savefig(out_file, dpi=dpi, bbox_inches="tight")
        print(f"[OK] Dendrograma guardado en {out_file}")
        plt.close(fig)
    else:
        # Mostrar interactivamente
        plt.show()

    # Retornar información del clustering
    return {
        "Z": Z,  # Matriz de enlace (linkage matrix)
        "color_threshold": color_threshold,  # Umbral usado
        "order": D.get("leaves", [])  # Orden de hojas en dendrograma
    }
