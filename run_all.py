# C:\Bibliometria\run_all.py
from __future__ import annotations
import sys, subprocess, argparse
from pathlib import Path

PY = sys.executable  # .\venv\Scripts\python.exe si el venv está activado

def run(*cmd):
    print(">", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)

def main():
    ap = argparse.ArgumentParser(description="Runner de todos los requerimientos (1→5) en orden.")
    ap.add_argument("--bib", type=str, default="", help="Ruta al .bib (si se omite, usa el default)")
    ap.add_argument("--req2", type=int, nargs="+", default=[0,3,7], help="Índices para Req2 (mín. 2)")
    ap.add_argument("--req4n", type=int, default=25, help="Número de abstracts para Req4")
    ap.add_argument("--wcmax", type=int, default=150, help="Máx. palabras en wordcloud (Req5)")
    ap.add_argument("--topj", type=int, default=8, help="Top N revistas en timeline por journal (Req5)")
    args = ap.parse_args()

    # # 1) Req1
    # print("\n[REQ1] Scrapers + scripts base")
    # run(PY, "main.py", "req1")

    # 2) Req2
    print("\n[REQ2] Similitud textual")
    if len(args.req2) < 2:
        raise SystemExit("Req2 necesita ≥2 índices, ej: --req2 0 3 7")
    run(PY, "main.py", "req2", *[str(i) for i in args.req2])

    # 3) Req3
    print("\n[REQ3] Frecuencias + términos asociados + precisión")
    req3_cmd = [PY, "main.py", "req3", "--max-terms", "15", "--min-df", "2", "--thr", "0.50"]
    if args.bib:
        req3_cmd += ["--bib", args.bib]
    run(*req3_cmd)

    # 4) Req4
    print("\n[REQ4] Clustering jerárquico + dendrogramas")
    req4_cmd = [PY, "main.py", "req4", "--n", str(args.req4n)]
    if args.bib:
        req4_cmd += ["--bib", args.bib]
    run(*req4_cmd)

    # 5) Req5
    print("\n[REQ5] Heatmap + WordCloud + Timelines + PDF")
    req5_cmd = [PY, "main.py", "req5", "--wc-max", str(args.wcmax), "--topj", str(args.topj)]
    if args.bib:
        req5_cmd += ["--bib", args.bib]
    run(*req5_cmd)

    print("\n=== Flujo completo finalizado ===")

if __name__ == "__main__":
    main()
