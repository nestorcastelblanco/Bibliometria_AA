from __future__ import annotations
import sys
import subprocess
import argparse
from pathlib import Path

venv_python = sys.executable  # C:\Bibliometria\venv\Scripts\python.exe

# ===================================================================
# BLOQUE DE AUTOMATIZACIÓN INICIAL (Req. 1 y Seguimiento 1)
# ===================================================================
def ejecutar_scripts_base():
    scripts = [
        r"C:\Bibliometria\requirement_1\scrapers\acm_scraper.py",
        r"C:\Bibliometria\requirement_1\scrapers\sage_scraper.py",
        r"C:\Bibliometria\requirement_1\unificar.py",
        r"C:\Bibliometria\Seguimiento_1\algoritmos_ordenamiento.py",
        r"C:\Bibliometria\Seguimiento_1\author_range.py",
        r"C:\Bibliometria\Seguimiento_1\stats_algoritmos.py",
    ]
    for script in scripts:
        print(f"[RUN] Ejecutando: {script}")
        try:
            subprocess.run([venv_python, script], check=True)
            print(f"[OK] Finalizado: {script}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] en {script}\n{e}")

# ===================================================================
# REQ. 2 – Similitud textual (detecta run() CSV o run_from_bib() BIB)
# ===================================================================
def ejecutar_req2(indices: list[int]):
    print(f"[RUN] Ejecutando Requerimiento 2 con índices: {indices}")
    import requirement_2.run_similarity as rs
    if hasattr(rs, "run"):
        print("[INFO] Detectado run_similarity.run (modo CSV).")
        path = rs.run(indices)
    elif hasattr(rs, "run_from_bib"):
        print("[INFO] Detectado run_similarity.run_from_bib (modo BIB).")
        path = rs.run_from_bib(indices)
    else:
        raise RuntimeError("El módulo run_similarity no expone ni run() ni run_from_bib().")

    print(f"[OK] Archivo generado: {path}")

    # Resumen en consola (subproceso para evitar conflicto de argparse)
    try:
        subprocess.run(
            [venv_python, "-m", "requirement_2.console_report", "--json", path, "--top", "10"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("[Aviso] No se pudo generar el resumen en consola automáticamente:", e)

# ===================================================================
# REQ. 3 – Frecuencias + términos asociados + precisión
# ===================================================================
def ejecutar_req3(bib: Path | None = None, max_terms: int = 15, min_df: int = 2, thr: float = 0.50):
    from requirement_3.run_req3 import run_req3, print_console_summary
    from requirement_3.data_loader import DEFAULT_BIB
    bib_path = bib if bib else DEFAULT_BIB
    print(f"[RUN] Ejecutando Requerimiento 3 (frecuencias y términos asociados)...")
    out = run_req3(bib_path=bib_path, max_auto_terms=max_terms, min_df=min_df, threshold=thr)
    print(f"[OK] Resultados guardados en: {out}")
    print_console_summary(Path(out))

# ===================================================================
# REQ. 4 – Clustering jerárquico + dendrogramas
# ===================================================================
def ejecutar_req4(bib: Path | None = None, n_samples: int = 25):
    from requirement_4.run_req4 import run_req4
    from requirement_3.data_loader import DEFAULT_BIB
    bib_path = bib if bib else DEFAULT_BIB
    print(f"[RUN] Ejecutando Requerimiento 4 (clustering jerárquico)...")
    run_req4(bib_path=bib_path, n_samples=n_samples)
    print("[OK] Dendrogramas generados en data/processed/.")

# ===================================================================
# REQ. 5 – Visual analytics (mapa de calor, wordcloud, líneas de tiempo, PDF)
# ===================================================================
def ejecutar_req5(bib: Path | None = None, affmap: Path | None = None, wc_max: int = 150, topj: int = 8):
    from requirement_5.run_req5 import run_req5
    from requirement_5.data_loader5 import DEFAULT_BIB
    bib_path = bib if bib else DEFAULT_BIB
    print(f"[RUN] Ejecutando Requerimiento 5 (mapa de calor, nube y timeline + PDF)...")
    out = run_req5(bib_path=bib_path, affiliations_map_csv=affmap, wordcloud_max_words=wc_max, journals_top_n=topj)
    print("[OK] Archivos generados:")
    for k, v in out.items():
        print(f"  - {k}: {v}")

# ===================================================================
# INTERFAZ PRINCIPAL (CLI)
# ===================================================================
def main():
    parser = argparse.ArgumentParser(description="Proyecto Bibliometría – Ejecución de Requerimientos")
    sub = parser.add_subparsers(dest="cmd")

    # Requerimiento 1
    sub.add_parser("req1", help="Ejecuta los scrapers y scripts base")

    # Requerimiento 2
    p2 = sub.add_parser("req2", help="Similitud textual sobre abstracts")
    p2.add_argument("indices", nargs="+", type=int, help="Índices del dataset a comparar")

    # Requerimiento 3
    p3 = sub.add_parser("req3", help="Frecuencias por categoría + auto términos + evaluación")
    p3.add_argument("--bib", type=str, default=None, help="Ruta al archivo .bib (por defecto usa productos_unificados.bib)")
    p3.add_argument("--max-terms", type=int, default=15, help="Máximo de términos auto-generados")
    p3.add_argument("--min-df", type=int, default=2, help="Mínimo de documentos donde aparece el término")
    p3.add_argument("--thr", type=float, default=0.50, help="Umbral de similitud para marcar término relevante")

    # Requerimiento 4
    p4 = sub.add_parser("req4", help="Clustering jerárquico de abstracts y generación de dendrogramas")
    p4.add_argument("--bib", type=str, default=None, help="Ruta al .bib (por defecto usa productos_unificados.bib)")
    p4.add_argument("--n", type=int, default=25, help="Número de abstracts a agrupar (ej.: 25)")

    # Requerimiento 5
    p5 = sub.add_parser("req5", help="Mapa de calor (país), WordCloud, líneas temporales y PDF")
    p5.add_argument("--bib", type=str, default=None, help="Ruta al .bib (por defecto usa productos_unificados.bib)")
    p5.add_argument("--affmap", type=str, default="", help="CSV institution,country (opcional)")
    p5.add_argument("--wc-max", type=int, default=150, help="Máx. palabras en la nube de palabras")
    p5.add_argument("--topj", type=int, default=8, help="Top N revistas en timeline por journal")

    args = parser.parse_args()

    if args.cmd == "req1":
        ejecutar_scripts_base()

    elif args.cmd == "req2":
        ejecutar_req2(args.indices)

    elif args.cmd == "req3":
        bib = Path(args.bib) if args.bib else None
        ejecutar_req3(bib=bib, max_terms=args.max_terms, min_df=args.min_df, thr=args.thr)

    elif args.cmd == "req4":
        bib = Path(args.bib) if args.bib else None
        ejecutar_req4(bib=bib, n_samples=args.n)

    elif args.cmd == "req5":
        bib = Path(args.bib) if args.bib else None
        aff = Path(args.affmap) if args.affmap else None
        ejecutar_req5(bib=bib, affmap=aff, wc_max=args.wc_max, topj=args.topj)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
