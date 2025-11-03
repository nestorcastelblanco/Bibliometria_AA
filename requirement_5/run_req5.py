"""
Módulo de orquestación del Requerimiento 5: Visualizaciones avanzadas y reportes PDF.

Ejecuta el pipeline completo de análisis visual bibliométrico:
1. Heatmap geográfico del primer autor (mapa mundial o barras)
2. Word cloud de abstracts + keywords
3. Líneas temporales (por año y por revista)
4. Exportación a PDF único con todas las visualizaciones

Genera archivos PNG individuales + HTML interactivo + PDF consolidado.
"""
from __future__ import annotations
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

from requirement_5.data_loader5 import load_bib_dataframe, DEFAULT_BIB, PROJECT_ROOT
from requirement_5.geo import compute_country_counts, plot_world_heatmap
from requirement_5.wordcloud_gen import make_wordcloud
from requirement_5.timeline import plot_year_series, plot_journal_series

# Directorio de salida para visualizaciones
OUT_DIR = PROJECT_ROOT / "requirement_5"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def run_req5(
    bib_path: Path = DEFAULT_BIB,
    affiliations_map_csv: Path | None = None,
    wordcloud_max_words: int = 150,
    journals_top_n: int = 8,
) -> dict:
    """
    Ejecuta pipeline completo del Requerimiento 5: visualizaciones avanzadas + PDF.
    
    Proceso de 4 etapas principales:
    1. Heatmap geográfico (primer autor por país)
    2. Word cloud (abstracts + keywords)
    3. Líneas temporales (año y revista)
    4. Exportación a PDF consolidado
    
    Args:
        bib_path (Path, optional): Ruta al archivo BibTeX. Default: DEFAULT_BIB
        affiliations_map_csv (Path | None, optional): CSV con mapeo institution→country.
            Default: None (usa solo pycountry)
        wordcloud_max_words (int, optional): Máximo de palabras en nube. Default: 150
        journals_top_n (int, optional): Top N revistas para serie temporal. Default: 8
    
    Returns:
        dict: Rutas de archivos generados con keys:
            - heatmap_png: Mapa/gráfico de países PNG
            - heatmap_html: Mapa interactivo HTML (solo si Plotly disponible)
            - wordcloud_png: Nube de palabras PNG
            - timeline_year_png: Serie temporal por año PNG
            - timeline_journal_png: Serie temporal por revista PNG
            - pdf: Reporte PDF consolidado
    
    Example:
        >>> result = run_req5(
        ...     bib_path=Path("data/refs.bib"),
        ...     affiliations_map_csv=Path("data/affil_map.csv"),
        ...     wordcloud_max_words=100,
        ...     journals_top_n=10
        ... )
        >>> print(result["pdf"])
        '/path/to/requirement_5/req5_report.pdf'
    
    Archivos generados:
        - requirement_5/req5_heatmap.png: Visualización geográfica
        - requirement_5/req5_heatmap.html: Mapa interactivo (si Plotly)
        - requirement_5/req5_wordcloud.png: Nube de palabras
        - requirement_5/req5_timeline_year.png: Publicaciones por año
        - requirement_5/req5_timeline_journal.png: Publicaciones por revista
        - requirement_5/req5_report.pdf: PDF con todas las imágenes
    
    Notas:
        - Requiere: matplotlib, PIL, plotly (opcional), wordcloud
        - PDF contiene las 4 visualizaciones PNG en páginas separadas
        - HTML solo se genera si Plotly está disponible
        - Figuras se adaptan al tamaño de imagen para preservar calidad
    """
    print("[RUN] Requerimiento 5 – Visual analytics")

    # Cargar datos BibTeX
    df = load_bib_dataframe(bib_path)
    
    # ========== ETAPA 1: Heatmap geográfico (primer autor) ==========
    counts = compute_country_counts(df, affiliations_map_csv)
    geo_png  = OUT_DIR / "req5_heatmap.png"
    geo_html = OUT_DIR / "req5_heatmap.html"
    _ = plot_world_heatmap(counts, geo_png, geo_html)

    # ========== ETAPA 2: Nube de palabras (abstracts + keywords) ==========
    wc_png = OUT_DIR / "req5_wordcloud.png"
    make_wordcloud(df, wc_png, max_words=wordcloud_max_words)

    # ========== ETAPA 3: Líneas temporales ==========
    year_png    = OUT_DIR / "req5_timeline_year.png"
    journal_png = OUT_DIR / "req5_timeline_journal.png"
    plot_year_series(df, year_png)
    plot_journal_series(df, journal_png, top_n=journals_top_n)

    # ========== ETAPA 4: Exportar a PDF único ==========
    pdf_path = OUT_DIR / "req5_report.pdf"
    from PIL import Image
    
    with PdfPages(pdf_path) as pdf:
        # Iterar sobre las 4 visualizaciones principales
        for fig_path in (geo_png, wc_png, year_png, journal_png):
            if fig_path.exists():
                # Cargar imagen PNG
                img = Image.open(fig_path)
                
                # Crear figura matplotlib del tamaño exacto de la imagen
                import matplotlib.pyplot as plt
                fig = plt.figure(
                    figsize=(img.width/100, img.height/100), 
                    dpi=100
                )
                
                # Mostrar imagen sin ejes
                plt.imshow(img)
                plt.axis("off")
                
                # Guardar en PDF
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

    # Resumen de archivos generados
    print("[OK] Archivos generados en data/processed/:")
    print(f"- {geo_png.name} (+ {geo_html.name})")
    print(f"- {wc_png.name}")
    print(f"- {year_png.name}")
    print(f"- {journal_png.name}")
    print(f"- {pdf_path.name}")
    
    return {
        "heatmap_png": str(geo_png),
        "heatmap_html": str(geo_html),
        "wordcloud_png": str(wc_png),
        "timeline_year_png": str(year_png),
        "timeline_journal_png": str(journal_png),
        "pdf": str(pdf_path),
    }

if __name__ == "__main__":
    """
    Interfaz de línea de comandos para ejecutar Requerimiento 5.
    
    Uso:
        python -m requirement_5.run_req5 [opciones]
    
    Opciones:
        --bib PATH: Ruta al archivo BibTeX (default: data/processed/biblioteca.bib)
        --affmap PATH: CSV con mapeo institution→country (opcional)
        --wc-max N: Máximo de palabras en word cloud (default: 150)
        --topj N: Top N revistas para serie temporal (default: 8)
    
    Examples:
        # Ejecución básica con defaults
        $ python -m requirement_5.run_req5
        
        # Con archivo BibTeX personalizado
        $ python -m requirement_5.run_req5 --bib data/my_refs.bib
        
        # Con mapeo de afiliaciones y 100 palabras max
        $ python -m requirement_5.run_req5 --affmap data/affil.csv --wc-max 100
        
        # Top 12 revistas en serie temporal
        $ python -m requirement_5.run_req5 --topj 12
    """
    import argparse
    
    ap = argparse.ArgumentParser(
        description="Req 5: Heatmap país (primer autor), WordCloud y líneas temporales + PDF"
    )
    ap.add_argument(
        "--bib", 
        type=str, 
        default=str(DEFAULT_BIB), 
        help="Ruta al archivo .bib de entrada"
    )
    ap.add_argument(
        "--affmap", 
        type=str, 
        default="", 
        help="CSV con columnas: institution,country (mapeo manual de afiliaciones)"
    )
    ap.add_argument(
        "--wc-max", 
        type=int, 
        default=150, 
        help="Máximo número de palabras a mostrar en word cloud"
    )
    ap.add_argument(
        "--topj", 
        type=int, 
        default=8, 
        help="Top N revistas a mostrar en serie temporal por journal"
    )
    
    args = ap.parse_args()

    # Preparar ruta opcional de mapeo de afiliaciones
    aff = Path(args.affmap) if args.affmap else None
    
    # Ejecutar pipeline completo
    run_req5(
        bib_path=Path(args.bib),
        affiliations_map_csv=aff,
        wordcloud_max_words=args.wc_max,
        journals_top_n=args.topj,
    )
