from __future__ import annotations
import sys
import subprocess
import argparse
from pathlib import Path
import os

venv_python = sys.executable  # C:\Bibliometria\venv\Scripts\python.exe

# ======== Consola Windows: forzar UTF-8 en todo el proceso ========
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")
# ================================================================

def run_py_utf8(args: list[str]):
    """
    Ejecuta python del venv con -X utf8 y variables de entorno correctas.
    'args' es la lista a partir de script o -m ... (sin el exe).
    """
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    cmd = [venv_python, "-X", "utf8"] + args
    return subprocess.run(cmd, check=True, env=env)

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
            run_py_utf8([script])
            print(f"[OK] Finalizado: {script}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] en {script}\n{e}")

# ===================================================================
# REQ. 2 – Similitud textual
# ===================================================================
def ejecutar_req2(indices: list[int]):
    print(f"[RUN] Ejecutando Requerimiento 2 con índices: {indices}")
    try:
        import importlib
        rs = importlib.import_module("requirement_2.run_similarity")
    except ModuleNotFoundError:
        PROJECT_ROOT = Path(__file__).resolve().parent
        sys.path.insert(0, str(PROJECT_ROOT))
        import importlib
        rs = importlib.import_module("requirement_2.run_similarity")

    if hasattr(rs, "run"):
        print("[INFO] Detectado run_similarity.run (modo CSV).")
        path = rs.run(indices)
    elif hasattr(rs, "run_from_bib"):
        print("[INFO] Detectado run_similarity.run_from_bib (modo BIB).")
        path = rs.run_from_bib(indices)
    else:
        raise RuntimeError("El módulo run_similarity no expone ni run() ni run_from_bib().")

    print(f"[OK] Archivo generado: {path}")

    # Reporte en consola (UTF-8 / ASCII-safe)
    try:
        run_py_utf8([
            "-m", "requirement_2.console_report",
            "--json", str(path), "--top", "10", "--ascii"  # quita --ascii si prefieres Unicode
        ])
    except subprocess.CalledProcessError as e:
        print("[Aviso] No se pudo generar el resumen en consola automáticamente:", e)

    # Extra: generar MD y CSV bien presentados para la web UI
    try:
        from requirement_2.reports import (
            _read_json, _detect_primary_algo, generate_markdown, generate_csv_top
        )
        data = _read_json(Path(path))
        algo = _detect_primary_algo(data.get("results", []), prefer=None)
        out_md  = Path("data/processed/reporte_similitud.md")
        out_csv = Path("data/processed/reporte_similitud_top.csv")
        generate_markdown(data, algo, top=10, out_md=out_md)
        generate_csv_top(data, algo, top=10, out_csv=out_csv)
        print(f"[OK] Reportes listos:\n  - {out_md}\n  - {out_csv}")
    except Exception as e:
        print("[Aviso] No se pudo generar el MD/CSV:", e)

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
# REQ. 5 – Visual analytics
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
# GRAFOS – Citaciones y Términos
# ===================================================================
def ejecutar_grafos_cit(bib: Path | None = None, min_sim: float = 0.35):
    from requirement_grafos.run_grafos import run_req_grafos_citas
    from requirement_3.data_loader import DEFAULT_BIB
    bib_path = bib if bib else DEFAULT_BIB
    print(f"[RUN] Grafos – Citaciones (dirigido) con min_sim={min_sim}")
    out = run_req_grafos_citas(bib=bib_path, min_sim=min_sim)
    print("[OK] Grafo de citaciones:", out)

def ejecutar_grafos_terms(
    bib: Path | None = None,
    terms_path: Path | None = None,
    min_df: int = 3,
    window: int = 30,
    min_cooc: int = 2
):
    from requirement_grafos.run_grafos import run_req_grafos_terminos
    from requirement_3.data_loader import DEFAULT_BIB, PROJECT_ROOT
    import json

    bib_path = bib if bib else DEFAULT_BIB

    if not terms_path:
        req3_results = PROJECT_ROOT / "requirement_3" / "req3_resultados.json"
        if req3_results.exists():
            print("[INFO] Cargando términos desde Requerimiento 3...")
            with open(req3_results, 'r', encoding='utf-8') as f:
                req3_data = json.load(f)
            seed_terms = req3_data.get('seed_words_normalized', [])
            auto_terms = req3_data.get('auto_terms', [])
            combined_terms = seed_terms + auto_terms
            print(f"[INFO] Usando {len(combined_terms)} términos del Req3 ({len(seed_terms)} semilla + {len(auto_terms)} automáticos)")
            temp_terms_file = PROJECT_ROOT / "data" / "processed" / "términos_grafos.json"
            with open(temp_terms_file, 'w', encoding='utf-8') as f:
                json.dump(combined_terms, f, ensure_ascii=False, indent=2)
            terms_path = temp_terms_file
        else:
            print(f"[AVISO] No se encontró {req3_results}, usando todos los términos del corpus")

    print(f"[RUN] Grafos – Términos (no dirigido) df>={min_df}, window={window}, min_cooc={min_cooc}")
    out = run_req_grafos_terminos(
        bib=bib_path,
        terms_path=terms_path,
        min_df=min_df,
        window=window,
        min_cooc=min_cooc
    )
    print("[OK] Grafo de términos:", out)

# ===================================================================
# INTERFAZ PRINCIPAL (CLI)
# ===================================================================
def main():
    parser = argparse.ArgumentParser(description="Proyecto Bibliometría – Ejecución de Requerimientos")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("req1", help="Ejecuta los scrapers y scripts base")

    p2 = sub.add_parser("req2", help="Similitud textual sobre abstracts")
    p2.add_argument("indices", nargs="+", type=int, help="Índices del dataset a comparar")

    p3 = sub.add_parser("req3", help="Frecuencias por categoría + auto términos + evaluación")
    p3.add_argument("--bib", type=str, default=None, help="Ruta al archivo .bib (por defecto usa productos_unificados.bib)")
    p3.add_argument("--max-terms", type=int, default=15, help="Máximo de términos auto-generados")
    p3.add_argument("--min-df", type=int, default=2, help="Mínimo de documentos donde aparece el término")
    p3.add_argument("--thr", type=float, default=0.50, help="Umbral de similitud para marcar término relevante")

    p4 = sub.add_parser("req4", help="Clustering jerárquico de abstracts y generación de dendrogramas")
    p4.add_argument("--bib", type=str, default=None, help="Ruta al .bib (por defecto usa productos_unificados.bib)")
    p4.add_argument("--n", type=int, default=25, help="Número de abstracts a agrupar (ej.: 25)")

    p5 = sub.add_parser("req5", help="Mapa de calor (país), WordCloud, líneas temporales y PDF")
    p5.add_argument("--bib", type=str, default=None, help="Ruta al .bib (por defecto usa productos_unificados.bib)")
    p5.add_argument("--affmap", type=str, default="", help="CSV institution,country (opcional)")
    p5.add_argument("--wc-max", type=int, default=150, help="Máx. palabras en la nube de palabras")
    p5.add_argument("--topj", type=int, default=8, help="Top N revistas en timeline por journal")

    pg1 = sub.add_parser("grafos_cit", help="Grafo de citaciones (dirigido) + Dijkstra/FW + SCC")
    pg1.add_argument("--bib", type=str, default=None, help="Ruta al .bib (por defecto usa productos_unificados.bib)")
    pg1.add_argument("--min-sim", type=float, default=0.35, help="Umbral de similitud para inferir aristas")

    pg2 = sub.add_parser("grafos_terms", help="Grafo de co-ocurrencia de términos (no dirigido)")
    pg2.add_argument("--bib", type=str, default=None, help="Ruta al .bib (por defecto usa productos_unificados.bib)")
    pg2.add_argument("--terms", type=str, default="", help="Ruta a JSON/TXT con términos (opcional)")
    pg2.add_argument("--min-df", type=int, default=3, help="Mínimo DF para incluir términos si no se pasan candidatos")
    pg2.add_argument("--window", type=int, default=30, help="Tamaño de ventana de co-ocurrencia")
    pg2.add_argument("--min-cooc", type=int, default=2, help="Co-ocurrencias mínimas para crear arista")

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
    elif args.cmd == "grafos_cit":
        bib = Path(args.bib) if args.bib else None
        ejecutar_grafos_cit(bib=bib, min_sim=args.min_sim)
    elif args.cmd == "grafos_terms":
        bib = Path(args.bib) if args.bib else None
        terms = Path(args.terms) if args.terms else None
        ejecutar_grafos_terms(bib=bib, terms_path=terms, min_df=args.min_df, window=args.window, min_cooc=args.min_cooc)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
