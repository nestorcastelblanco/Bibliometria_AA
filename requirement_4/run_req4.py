"""
Módulo de orquestación del Requerimiento 4: Clustering jerárquico y dendrogramas.

Ejecuta el pipeline completo de clustering de abstracts bibliométricos:
1. Carga abstracts desde BibTeX
2. Preprocesa texto (limpieza, tokenización)
3. Calcula matriz TF-IDF para Ward + matriz de similitud coseno para otros
4. Ward: Reducción SVD + distancia euclidiana
5. Complete/Average: Distancia coseno (1 - similitud)
6. Aplica clustering jerárquico (ward/complete/average)
7. Genera dendrogramas estéticos de alta calidad

Genera archivos PNG individuales para cada método de enlace.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List

from requirement_3.data_loader import load_bib_dataframe, DEFAULT_BIB  # carga abstracts desde .bib
from requirement_4.preprocess import preprocess_corpus
from requirement_4.similarity_matrix import build_similarity_matrix, similarity_to_distance
from requirement_4.clustering import run_hierarchical_clustering_pretty, run_ward_clustering_with_svd
from sklearn.feature_extraction.text import TfidfVectorizer

# Configuración de directorios
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "requirement_4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def _short_text(s: str, n: int = 52) -> str:
    """
    Trunca texto para etiquetas amigables en dendrograma.
    
    Args:
        s (str): Texto a truncar (típicamente título de paper)
        n (int, optional): Longitud máxima. Default: 52
    
    Returns:
        str: Texto truncado con '…' si excede longitud
    
    Example:
        >>> _short_text("A comprehensive study of machine learning algorithms", 30)
        'A comprehensive study of mac…'
    
    Notas:
        - Similar a _truncate de clustering.py pero con default 52
        - Elimina saltos de línea para etiquetas compactas
        - Usado para generar etiquetas "A0 — título truncado"
    """
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
    Ejecuta pipeline completo del Requerimiento 4: clustering jerárquico de abstracts.
    
    Proceso de 5 etapas principales:
    1. Carga abstracts desde BibTeX (con submuestreo opcional)
    2. Preprocesamiento de texto
    3. Construcción de matriz de similitud/distancia
    4. Clustering jerárquico con múltiples métodos
    5. Generación de dendrogramas PNG de alta calidad
    
    Args:
        bib_path (Path, optional): Ruta al archivo BibTeX. Default: DEFAULT_BIB
        n_samples (int, optional): Número máximo de abstracts a procesar (submuestreo).
            Default: 25. Útil para visualización legible
        methods (List[str] | None, optional): Métodos de enlace a comparar.
            Default: None → ['single', 'complete', 'average']
        use_titles_as_labels (bool, optional): Si True, etiquetas son "A0 — título truncado".
            Si False, solo "A0", "A1", etc. Default: True
        color_threshold (float | None, optional): Umbral de distancia para colorear clusters.
            None → usa 70% del máximo. Default: None
        leaf_font_size (int, optional): Tamaño de fuente de etiquetas de hojas. Default: 9
    
    Returns:
        dict: Resultados por método, con keys = método ('single', 'complete', 'average')
            Cada valor es dict con:
                - png: Ruta al archivo PNG generado
                - color_threshold: Umbral usado para colorear
                - leaf_order: Orden de hojas en dendrograma
    
    Example:
        >>> results = run_req4(
        ...     bib_path=Path("data/refs.bib"),
        ...     n_samples=30,
        ...     methods=["average", "complete"],
        ...     use_titles_as_labels=True
        ... )
        >>> results.keys()
        dict_keys(['average', 'complete'])
        >>> results['average']['png']
        '/path/to/requirement_4/dendrogram_average.png'
    
    Métodos de enlace comparados:
        - 'ward': Enlace Ward con SVD (minimiza varianza intra-cluster)
            * Ventajas: Clusters balanceados, dendrogramas cuadrados, robusto
            * Desventajas: Requiere reducción SVD, usa distancias euclidianas
        
        - 'complete': Enlace completo (distancia máxima entre clusters)
            * Ventajas: Forma clusters compactos y bien separados
            * Desventajas: Sensible a outliers
        
        - 'average': Enlace promedio (distancia media entre clusters)
            * Ventajas: Balanceado, robusto, recomendado para mayoría de casos
            * Desventajas: Computacionalmente más costoso
    
    Archivos generados:
        - requirement_4/dendrogram_ward.png: Dendrograma con enlace Ward (SVD)
        - requirement_4/dendrogram_complete.png: Dendrograma con enlace completo
        - requirement_4/dendrogram_average.png: Dendrograma con enlace promedio
    
    Notas:
        - n_samples recomendado: 15-30 para dendrogramas legibles
        - TF-IDF usa stop_words='english' para abstracts en inglés
        - Similitud coseno → distancia: dist = 1 - sim
        - color_threshold automático: 70% del máximo (regla empírica efectiva)
        - Títulos largos se truncan a max_label_len caracteres
        - Alta resolución: DPI 240 para publicaciones
    """
    print("[RUN] Requerimiento 4 – Clustering jerárquico de abstracts")

    # ========== ETAPA 1: Cargar abstracts desde BibTeX ==========
    df = load_bib_dataframe(bib_path)
    abstracts_all = [str(x) for x in df["abstract"].tolist() if isinstance(x, str)]
    titles_all    = [str(x) for x in df["title"].tolist()]

    # Submuestreo para visualización legible
    if len(abstracts_all) > n_samples:
        abstracts = abstracts_all[:n_samples]
        titles    = titles_all[:n_samples]
        print(f"[INFO] Se tomarán {n_samples} abstracts para la demostración.")
    else:
        abstracts = abstracts_all
        titles    = titles_all

    # ========== ETAPA 2: Preprocesamiento de texto ==========
    corpus_clean = preprocess_corpus(abstracts)

    # ========== ETAPA 3: Matriz TF-IDF y conversión a distancia ==========
    # Crear matriz TF-IDF (necesaria para Ward con SVD)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus_clean)
    
    # Para average y complete: usar similitud coseno → distancia
    sim = build_similarity_matrix(corpus_clean)
    dist = similarity_to_distance(sim)

    # ========== ETAPA 4: Preparar etiquetas ==========
    if use_titles_as_labels:
        # Etiquetas con títulos truncados: "A0 — título..."
        labels = [f"A{i} — {_short_text(t)}" for i, t in enumerate(titles)]
        left_margin = 0.32  # Margen extra para títulos largos
        max_label_len = 52
    else:
        # Etiquetas simples: "A0", "A1", ...
        labels = [f"A{i}" for i in range(len(abstracts))]
        left_margin = 0.22
        max_label_len = 42

    # ========== ETAPA 5: Clustering y dendrogramas ==========
    # Métodos a comparar
    if methods is None:
        methods = ["ward", "complete", "average"]

    results: Dict[str, Any] = {}
    
    # Generar dendrograma para cada método
    for m in methods:
        out_file = OUT_DIR / f"dendrogram_{m}.png"
        print(f"[RUN] Dendrograma → método: {m}")
        
        # Ward requiere tratamiento especial (SVD + euclidiana)
        if m == "ward":
            info = run_ward_clustering_with_svd(
                tfidf_matrix=tfidf_matrix,
                labels=labels,
                n_components=min(50, len(abstracts) - 1),  # SVD components
                title=f"Dendrograma — Método: Ward (SVD)",
                out_file=str(out_file),
                color_threshold=color_threshold,
                leaf_font_size=leaf_font_size,
                left_margin=left_margin,
                annotate_dist_axis=True,
                max_label_len=max_label_len,
            )
            results[m] = {
                "png": str(out_file),
                "color_threshold": info["color_threshold"],
                "leaf_order": info["order"],
                "svd_variance_explained": info["svd"].explained_variance_ratio_.sum()
            }
        else:
            # Average y Complete usan distancia coseno
            info = run_hierarchical_clustering_pretty(
                distance_matrix=dist,
                labels=labels,
                method=m,
                title=f"Dendrograma — Método: {m}",
                out_file=str(out_file),
                color_threshold=color_threshold,
                leaf_font_size=leaf_font_size,
                left_margin=left_margin,
                annotate_dist_axis=True,
                max_label_len=max_label_len,
            )
            results[m] = {
                "png": str(out_file),
                "color_threshold": info["color_threshold"],
                "leaf_order": info["order"],
            }

    print("[OK] Dendrogramas generados en:", OUT_DIR)
    return results


if __name__ == "__main__":
    """
    Interfaz de línea de comandos para ejecutar Requerimiento 4.
    
    Uso:
        python -m requirement_4.run_req4 [opciones]
    
    Opciones:
        --bib PATH: Ruta al archivo BibTeX (default: data/processed/biblioteca.bib)
        --n N: Número de abstracts a procesar (default: 25)
        --labels {titles|ids}: Tipo de etiquetas (default: titles)
        --thr FLOAT: Umbral de color para clusters (default: None = auto 70%)
        --font N: Tamaño de fuente de etiquetas (default: 9)
        --methods LIST: Métodos separados por coma (default: single,complete,average)
    
    Examples:
        # Ejecución básica con defaults
        $ python -m requirement_4.run_req4
        
        # 30 abstracts con solo IDs como etiquetas
        $ python -m requirement_4.run_req4 --n 30 --labels ids
        
        # Solo método average con umbral 0.5
        $ python -m requirement_4.run_req4 --methods average --thr 0.5
        
        # Fuente grande y 15 abstracts
        $ python -m requirement_4.run_req4 --n 15 --font 11
    """
    import argparse
    
    ap = argparse.ArgumentParser(
        description="Requerimiento 4: Clustering jerárquico y dendrogramas estéticos."
    )
    ap.add_argument(
        "--bib", 
        type=str, 
        default=str(DEFAULT_BIB), 
        help="Ruta al archivo .bib de entrada"
    )
    ap.add_argument(
        "--n", 
        type=int, 
        default=25, 
        help="Número de abstracts a agrupar (recomendado: 15-30 para legibilidad)"
    )
    ap.add_argument(
        "--labels", 
        choices=["titles", "ids"], 
        default="titles", 
        help="Tipo de etiquetas: 'titles' (A0 — título...) o 'ids' (A0, A1, ...)"
    )
    ap.add_argument(
        "--thr", 
        type=float, 
        default=None, 
        help="Umbral de distancia para colorear clusters (None = auto 70%% del máximo)"
    )
    ap.add_argument(
        "--font", 
        type=int, 
        default=9, 
        help="Tamaño de fuente de etiquetas de hojas"
    )
    ap.add_argument(
        "--methods", 
        type=str, 
        default="ward,complete,average", 
        help="Métodos de enlace separados por coma (ward, complete, average)"
    )

    args = ap.parse_args()
    
    # Parsear lista de métodos
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    
    # Ejecutar pipeline completo
    run_req4(
        bib_path=Path(args.bib),
        n_samples=args.n,
        methods=methods,
        use_titles_as_labels=(args.labels == "titles"),
        color_threshold=args.thr,
        leaf_font_size=args.font,
    )
