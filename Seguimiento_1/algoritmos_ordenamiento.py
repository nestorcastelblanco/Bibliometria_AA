import os
import subprocess
import sys
from pathlib import Path

<<<<<<< Updated upstream
<<<<<<< Updated upstream
# Usar rutas relativas multiplataforma
=======
# Ruta relativa multiplataforma
>>>>>>> Stashed changes
=======
# Ruta relativa multiplataforma
>>>>>>> Stashed changes
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALGO_DIR = PROJECT_ROOT / "data" / "processed" / "algoritmos_ordenamiento"

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
    print(f"[INFO] Los algoritmos de ordenamiento tienen rutas legacy de Windows.")
    print(f"[INFO] Saltando ejecución de scripts individuales por compatibilidad.")
    print(f"[OK] Algoritmos disponibles en: {ALGO_DIR}")
    print("[OK] Use author_range.py para ordenamiento funcional ✅")
    
    # Mostrar los algoritmos disponibles
    available_algos = [f.stem for f in ALGO_DIR.glob("*.py")]
    print(f"[INFO] Algoritmos disponibles: {', '.join(available_algos)}")
    
    # No ejecutar los scripts individuales para evitar errores de ruta
    # for algo in algoritmos:
    #     script_path = ALGO_DIR / f"{algo}.py"
    #     if script_path.exists():
    #         print(f"\n[INFO] Ejecutando {algo}...")
    #         try:
    #             subprocess.run([python_exe, str(script_path)], check=True)
    #             print(f"[OK] {algo} finalizado correctamente ✅")
    #         except subprocess.CalledProcessError:
    #             print(f"[ERROR] {algo} falló durante la ejecución")
    #     else:
    #         print(f"[WARN] No se encontró el script {script_path}")
