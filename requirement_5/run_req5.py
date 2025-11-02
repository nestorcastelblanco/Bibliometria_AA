from __future__ import annotations
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

from requirement_5.data_loader5 import load_bib_dataframe, DEFAULT_BIB, PROJECT_ROOT
from requirement_5.geo import compute_country_counts, plot_world_heatmap
from requirement_5.wordcloud_gen import make_wordcloud
from requirement_5.timeline import plot_year_series, plot_journal_series

OUT_DIR = PROJECT_ROOT / "requirement_5"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def run_req5(
    bib_path: Path = DEFAULT_BIB,
    affiliations_map_csv: Path | None = None,
    wordcloud_max_words: int = 150,
    journals_top_n: int = 8,
) -> dict:
    print("[RUN] Requerimiento 5 – Visual analytics")

    df = load_bib_dataframe(bib_path)
    # -------- 1) Heatmap geográfico (primer autor) ----------
    counts = compute_country_counts(df, affiliations_map_csv)
    geo_png  = OUT_DIR / "req5_heatmap.png"
    geo_html = OUT_DIR / "req5_heatmap.html"
    _ = plot_world_heatmap(counts, geo_png, geo_html)

    # -------- 2) Nube de palabras (abstracts + keywords) ----
    wc_png = OUT_DIR / "req5_wordcloud.png"
    make_wordcloud(df, wc_png, max_words=wordcloud_max_words)

    # -------- 3) Líneas temporales --------------------------
    year_png    = OUT_DIR / "req5_timeline_year.png"
    journal_png = OUT_DIR / "req5_timeline_journal.png"
    plot_year_series(df, year_png)
    plot_journal_series(df, journal_png, top_n=journals_top_n)

    # -------- 4) Exportar a PDF único -----------------------
    pdf_path = OUT_DIR / "req5_report.pdf"
    from PIL import Image
    with PdfPages(pdf_path) as pdf:
        for fig_path in (geo_png, wc_png, year_png, journal_png):
            if fig_path.exists():
                img = Image.open(fig_path)
                # Crear lienzo del tamaño de la imagen
                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(img.width/100, img.height/100), dpi=100)
                plt.imshow(img); plt.axis("off")
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

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
    import argparse
    ap = argparse.ArgumentParser(description="Req 5: Heatmap país (primer autor), WordCloud y líneas temporales + PDF")
    ap.add_argument("--bib", type=str, default=str(DEFAULT_BIB), help="Ruta al .bib")
    ap.add_argument("--affmap", type=str, default="", help="CSV institution,country (opcional)")
    ap.add_argument("--wc-max", type=int, default=150, help="Máx. palabras en la nube")
    ap.add_argument("--topj", type=int, default=8, help="Top N revistas en la serie por journal")
    args = ap.parse_args()

    aff = Path(args.affmap) if args.affmap else None
    run_req5(
        bib_path=Path(args.bib),
        affiliations_map_csv=aff,
        wordcloud_max_words=args.wc_max,
        journals_top_n=args.topj,
    )
