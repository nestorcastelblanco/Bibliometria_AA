import os
import subprocess
import sys

ALGO_DIR = r"C:\Bibliometria\data\processed\algoritmos_ordenamiento"

algoritmos = [
    "binary_insertion",
    "bitonic_sort",
    "bucket_sort",
    "comb_sort",
    "gnome_sort",
    "heap_sort",
    "pigeonhole",
    "quicksort",
    "radix_sort",
    "selection_sort",
    "timsort",
    "treesort"
]

if __name__ == "__main__":
    python_exe = sys.executable  # usa el python del entorno activo
    for algo in algoritmos:
        script_path = os.path.join(ALGO_DIR, f"{algo}.py")
        if os.path.exists(script_path):
            print(f"\n[INFO] Ejecutando {algo}...")
            try:
                subprocess.run([python_exe, script_path], check=True)
                print(f"[OK] {algo} finalizado correctamente ✅")
            except subprocess.CalledProcessError:
                print(f"[ERROR] {algo} falló durante la ejecución")
        else:
            print(f"[WARN] No se encontró el script {script_path}")
