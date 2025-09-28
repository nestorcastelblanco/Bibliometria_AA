import sys
import subprocess

venv_python = sys.executable  # apunta a C:\Bibliometria\venv\Scripts\python.exe

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
