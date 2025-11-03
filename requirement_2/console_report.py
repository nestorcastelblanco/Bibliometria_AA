"""
Script de generación de reporte de similitud en consola.

Genera resumen formateado de resultados de análisis de similitud textual
directamente en consola con estadísticas, distribución y ranking de pares.

Funcionalidades:
- Carga de resultados desde JSON
- Selección automática de algoritmo principal
- Cálculo de estadísticas descriptivas
- Distribución por rangos de similitud
- Ranking de top N pares más similares
- Formato legible en terminal

Parte del Requerimiento 2: Reporting y visualización de resultados.
"""
# requirement_2/console_report.py
from __future__ import annotations
import json, argparse
from pathlib import Path
from typing import Any, Dict, List, Optional
import statistics as stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = PROJECT_ROOT / "data" / "processed" / "similitud_req2.json"

PRIMARY_ORDER = [
    "GTE (coseno)",
    "SBERT (coseno)",
    "Coseno (TF-IDF)",
    "Jaccard (tokens)",
    "Damerau–Levenshtein (normalizada)",
    "Levenshtein (normalizada)",
]
"""
List[str]: Orden de prioridad para selección automática de algoritmo.

Cuando el usuario no especifica algoritmo, se elige el primero disponible
en este orden. Prioriza algoritmos de embeddings (más precisos) sobre clásicos.
"""

def pct(x: Optional[float]) -> str:
    """
    Formatea número decimal como porcentaje con 1 decimal.
    
    Args:
        x (Optional[float]): Valor decimal [0,1] o None
    
    Returns:
        str: Porcentaje formateado "X.X%" o "—" si None
    
    Example:
        >>> pct(0.8567)
        '85.7%'
        >>> pct(None)
        '—'
    """
    return "—" if x is None else f"{x*100:,.1f}%"

def read_json(path: Path) -> Dict[str, Any]:
    """
    Lee archivo JSON de resultados de similitud.
    
    Args:
        path (Path): Ruta al archivo JSON
    
    Returns:
        Dict[str, Any]: Diccionario con datos cargados
    
    Raises:
        FileNotFoundError: Si el archivo no existe
        json.JSONDecodeError: Si el JSON es inválido
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_algo(results: List[Dict[str, Any]], prefer: Optional[str]) -> str:
    """
    Detecta o selecciona algoritmo principal para reporte.
    
    Si el usuario especifica algoritmo y existe en resultados, lo usa.
    Si no, selecciona automáticamente según PRIMARY_ORDER.
    
    Args:
        results (List[Dict[str, Any]]): Lista de resultados de pares
        prefer (Optional[str]): Algoritmo preferido por usuario o None
    
    Returns:
        str: Nombre del algoritmo seleccionado
    
    Raises:
        ValueError: Si no se encuentran algoritmos en resultados
    
    Estrategia:
        1. Si prefer especificado y existe: usar ese
        2. Si no: buscar primer algoritmo de PRIMARY_ORDER presente
        3. Fallback: primer algoritmo encontrado en cualquier resultado
        4. Si nada: error
    
    Example:
        >>> results = [{"scores": {"GTE (coseno)": 0.8, "Jaccard (tokens)": 0.5}}]
        >>> detect_algo(results, None)
        'GTE (coseno)'
        >>> detect_algo(results, "Jaccard (tokens)")
        'Jaccard (tokens)'
    """
    if prefer:
        if any(prefer in r.get("scores", {}) for r in results):
            return prefer
    for cand in PRIMARY_ORDER:
        if any(cand in r.get("scores", {}) for r in results):
            return cand
    # fallback
    for r in results:
        if r.get("scores"):
            return list(r["scores"].keys())[0]
    raise ValueError("No se encontraron algoritmos en los resultados.")

def flat_scores(results: List[Dict[str, Any]], algo: str) -> List[float]:
    """
    Extrae lista plana de scores para un algoritmo específico.
    
    Args:
        results (List[Dict[str, Any]]): Lista de resultados de pares
        algo (str): Nombre del algoritmo
    
    Returns:
        List[float]: Lista de scores disponibles para ese algoritmo
    
    Notas:
        - Filtra pares donde el algoritmo no tiene score (None)
        - Convierte todos los scores a float
        - Útil para cálculo de estadísticas agregadas
    """
    vals = []
    for r in results:
        s = r["scores"].get(algo)
        if s is not None:
            vals.append(float(s))
    return vals

def compute_stats(vals: List[float]) -> Dict[str, Any]:
    """
    Calcula estadísticas descriptivas de lista de scores.
    
    Args:
        vals (List[float]): Lista de scores de similitud
    
    Returns:
        Dict[str, Any]: Estadísticas calculadas
            - n: Cantidad de valores
            - min: Valor mínimo
            - max: Valor máximo
            - mean: Promedio aritmético
            - median: Mediana
    
    Example:
        >>> compute_stats([0.2, 0.5, 0.8, 0.9])
        {'n': 4, 'min': 0.2, 'max': 0.9, 'mean': 0.6, 'median': 0.65}
        >>> compute_stats([])
        {'n': 0, 'min': None, 'max': None, 'mean': None, 'median': None}
    """
    if not vals:
        return {"n": 0, "min": None, "max": None, "mean": None, "median": None}
    return {
        "n": len(vals),
        "min": min(vals),
        "max": max(vals),
        "mean": sum(vals)/len(vals),
        "median": stats.median(vals),
    }

def buckets(vals: List[float]) -> Dict[str, int]:
    """
    Agrupa scores en buckets/rangos de similitud.
    
    Args:
        vals (List[float]): Lista de scores en [0, 1]
    
    Returns:
        Dict[str, int]: Conteo por rango
            - "≥0.80": Alta similitud
            - "0.60–0.79": Similitud moderada-alta
            - "0.40–0.59": Similitud moderada
            - "0.20–0.39": Similitud baja
            - "<0.20": Muy baja similitud
    
    Example:
        >>> buckets([0.1, 0.5, 0.7, 0.85, 0.9])
        {'≥0.80': 2, '0.60–0.79': 1, '0.40–0.59': 1, 
         '0.20–0.39': 0, '<0.20': 1}
    
    Notas:
        - Rangos diseñados para análisis de similitud textual
        - ≥0.80 típicamente indica pares muy relacionados
        - <0.20 típicamente indica pares no relacionados
    """
    b = {"≥0.80":0, "0.60–0.79":0, "0.40–0.59":0, "0.20–0.39":0, "<0.20":0}
    for v in vals:
        if v >= 0.80: b["≥0.80"] += 1
        elif v >= 0.60: b["0.60–0.79"] += 1
        elif v >= 0.40: b["0.40–0.59"] += 1
        elif v >= 0.20: b["0.20–0.39"] += 1
        else: b["<0.20"] += 1
    return b

def rank(results: List[Dict[str, Any]], algo: str, top: int) -> List[Dict[str, Any]]:
    """
    Ordena pares por similitud descendente y retorna top N.
    
    Args:
        results (List[Dict[str, Any]]): Lista de resultados de pares
        algo (str): Nombre del algoritmo para ordenar
        top (int): Cantidad de pares a retornar
    
    Returns:
        List[Dict[str, Any]]: Top N pares más similares
    
    Example:
        >>> results = [
        ...     {"i": 0, "j": 1, "scores": {"algo": 0.5}},
        ...     {"i": 0, "j": 2, "scores": {"algo": 0.9}},
        ...     {"i": 1, "j": 2, "scores": {"algo": 0.3}}
        ... ]
        >>> rank(results, "algo", 2)
        [{"i": 0, "j": 2, "scores": {"algo": 0.9}},
         {"i": 0, "j": 1, "scores": {"algo": 0.5}}]
    
    Notas:
        - Ordena descendente (mayor similitud primero)
        - Pares sin score para el algoritmo se tratan como 0.0
        - Retorna mínimo entre top y len(results)
    """
    ranked = sorted(results, key=lambda r: (r["scores"].get(algo) or 0.0), reverse=True)
    return ranked[:min(top, len(ranked))]

def main():
    """
    Función principal para ejecución desde línea de comandos.
    
    Parsea argumentos CLI, carga datos JSON, calcula estadísticas y
    genera reporte formateado en consola.
    
    Argumentos CLI:
        --json: Ruta al archivo JSON (default: data/processed/similitud_req2.json)
        --algo: Algoritmo principal (default: auto-selección)
        --top: Cantidad de top pares a mostrar (default: 10)
    
    Output en consola:
        ================= Requerimiento 2 — Resumen =================
        Algoritmo principal: <nombre>
        Artículos seleccionados: [índices]
        Pares comparados: <N>
        --------------------------------------------------------------
        Estadísticas → media: X% | mediana: X% | min: X% | max: X%
        Distribución:
          ≥0.80: N, 0.60–0.79: N, ...
        --------------------------------------------------------------
        Top N pares por <algoritmo>:
        1. (i,j)  XX.X%
           • título artículo i
           • título artículo j
        ...
        ==============================================================
    
    Example:
        $ python console_report.py --algo "GTE (coseno)" --top 5
        $ python console_report.py --json custom.json
    """
    ap = argparse.ArgumentParser(
        description="Resumen en consola del Requerimiento 2 (porcentajes, ranking y estadísticas)."
    )
    ap.add_argument("--json", default=str(DEFAULT_JSON), help="Ruta a similitud_req2.json")
    ap.add_argument("--algo", default=None, help="Algoritmo principal (si se omite, se elige automáticamente)")
    ap.add_argument("--top", type=int, default=10, help="Cantidad de pares a mostrar")
    args = ap.parse_args()

    data = read_json(Path(args.json))
    selected = data.get("selected", [])
    results  = data.get("results", [])
    if not results:
        print("No hay resultados en el JSON. Ejecuta primero requirement_2.run_similarity.")
        return

    algo = detect_algo(results, args.algo)
    vals = flat_scores(results, algo)
    st = compute_stats(vals)
    dist = buckets(vals)
    topN = rank(results, algo, args.top)

    # ===== Salida en consola =====
    print("\n================= Requerimiento 2 — Resumen =================")
    print(f"Algoritmo principal: {algo}")
    print(f"Artículos seleccionados: {[it['index'] for it in selected]}")
    print(f"Pares comparados: {len(results)}")
    print("--------------------------------------------------------------")
    print(f"Estadísticas →  media: {pct(st['mean'])} | mediana: {pct(st['median'])} "
          f"| min: {pct(st['min'])} | max: {pct(st['max'])}")
    print("Distribución:")
    print(f"  ≥0.80: {dist['≥0.80']},  0.60–0.79: {dist['0.60–0.79']},  0.40–0.59: {dist['0.40–0.59']},  "
          f"0.20–0.39: {dist['0.20–0.39']},  <0.20: {dist['<0.20']}")
    print("--------------------------------------------------------------")
    print(f"Top {len(topN)} pares por {algo}:")
    for i, r in enumerate(topN, 1):
        s = r["scores"].get(algo)
        t1 = (r.get("title_i") or "").strip().replace("\n", " ")
        t2 = (r.get("title_j") or "").strip().replace("\n", " ")
        print(f"{i:>2}. ({r['i']},{r['j']})  {pct(s)}")
        print(f"    • {t1}")
        print(f"    • {t2}")
    print("==============================================================\n")

if __name__ == "__main__":
    main()
