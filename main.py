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
# REQUERIMIENTO 2 – Similitud textual
# Detecta automáticamente si el módulo expone run() (CSV) o run_from_bib() (BIB)
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

    # <-- NUEVO: llamar el reporte en subproceso para que use sus propios args
    import subprocess, sys
    venv_python = sys.executable
    try:
        subprocess.run(
            [venv_python, "-m", "requirement_2.console_report", "--json", path, "--top", "10"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("[Aviso] No se pudo generar el resumen en consola automáticamente:", e)

# ===================================================================
# REQUERIMIENTO 3 – Frecuencias + términos asociados + precisión
# ===================================================================
def ejecutar_req3(bib: Path | None = None, max_terms: int = 15, min_df: int = 2, thr: float = 0.50):
    from requirement_3.run_req3 import run_req3, print_console_summary, DEFAULT_BIB
    bib_path = bib if bib else DEFAULT_BIB
    print(f"[RUN] Ejecutando Requerimiento 3 (frecuencias y términos asociados)...")
    out = run_req3(bib_path=bib_path, max_auto_terms=max_terms, min_df=min_df, threshold=thr)
    print(f"[OK] Resultados guardados en: {out}")
    print_console_summary(Path(out))

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

    args = parser.parse_args()

    if args.cmd == "req1":
        ejecutar_scripts_base()
    elif args.cmd == "req2":
        ejecutar_req2(args.indices)
    elif args.cmd == "req3":
        bib = Path(args.bib) if args.bib else None
        ejecutar_req3(bib=bib, max_terms=args.max_terms, min_df=args.min_df, thr=args.thr)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
