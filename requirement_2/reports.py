from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import statistics as stats
import argparse
import csv
from requirement_2.explainers import appendix_markdown

# Rutas robustas
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = PROJECT_ROOT / "data" / "processed" / "similitud_req2.json"
DEFAULT_MD   = PROJECT_ROOT / "data" / "processed" / "reporte_similitud.md"
DEFAULT_CSV  = PROJECT_ROOT / "data" / "processed" / "reporte_similitud_top.csv"

"""
Módulo de generación de reportes de similitud en múltiples formatos.

Genera reportes comprehensivos de análisis de similitud textual en:
- Markdown: Reporte completo con estadísticas, ranking y apéndice explicativo
- CSV: Tabla de top N pares más similares para análisis externo
- Consola: Resumen formateado en terminal

Funcionalidades:
- Selección automática de algoritmo principal
- Estadísticas descriptivas (media, mediana, min, max)
- Distribución por rangos de similitud
- Ranking de pares más similares
- Comparación multi-algoritmo
- Apéndice educativo con explicaciones

Parte del Requerimiento 2: Reporting y documentación de resultados.
"""
from requirement_2.explainers import appendix_markdown

# Rutas robustas
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = PROJECT_ROOT / "data" / "processed" / "similitud_req2.json"
DEFAULT_MD   = PROJECT_ROOT / "data" / "processed" / "reporte_similitud.md"
DEFAULT_CSV  = PROJECT_ROOT / "data" / "processed" / "reporte_similitud_top.csv"

# Prioridad de "algoritmo principal" si no se especifica --algo
PRIMARY_ORDER = [
    "GTE (coseno)",
    "SBERT (coseno)",
    "Coseno (TF-IDF)",
    "Jaccard (tokens)",
    "Damerau–Levenshtein (normalizada)",
    "Levenshtein (normalizada)",
]
"""
List[str]: Orden de prioridad para selección de algoritmo principal.

Define qué algoritmo usar cuando el usuario no especifica uno.
Prioriza embeddings de IA (mayor precisión semántica) sobre clásicos.
"""

def _pct(x: Optional[float]) -> str:
    """Formatea decimal como porcentaje con 1 decimal."""

def _pct(x: Optional[float]) -> str:
    if x is None:
        return "—"
    return f"{x*100:,.1f}%"

def _read_json(path: Path) -> Dict[str, Any]:
    """
    Lee archivo JSON de resultados de similitud.
    
    Args:
        path (Path): Ruta al archivo JSON
    
    Returns:
        Dict[str, Any]: Diccionario con datos cargados
    
    Raises:
        FileNotFoundError: Si el archivo no existe
    """
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el JSON: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _detect_primary_algo(results: List[Dict[str, Any]], prefer: Optional[str]) -> str:
    """
    Detecta algoritmo principal para reportes según preferencia o auto-selección.
    
    Args:
        results (List[Dict[str, Any]]): Lista de resultados de pares
        prefer (Optional[str]): Algoritmo preferido por usuario o None
    
    Returns:
        str: Nombre del algoritmo seleccionado
    
    Raises:
        ValueError: Si no se encuentran algoritmos en resultados
    
    Estrategia:
        1. Si prefer existe en resultados: usar ese
        2. Si no: primer algoritmo de PRIMARY_ORDER presente
        3. Fallback: primer algoritmo en cualquier resultado
    """
    # Si el usuario especifica y existe, usarlo
    if prefer:
        # verificar existencia en algún result
        for r in results:
            if prefer in r.get("scores", {}):
                return prefer
        # si no existe, seguimos a autoselección
    # Autoselección: primer algoritmo de PRIMARY_ORDER presente en results
    for candidate in PRIMARY_ORDER:
        for r in results:
            if candidate in r.get("scores", {}):
                return candidate
    # Fallback: cualquier clave que exista
    for r in results:
        sc = r.get("scores", {})
        if sc:
            return list(sc.keys())[0]
    raise ValueError("No se encuentran algoritmos de similitud en 'results'.")

def _flat_scores_for_algo(results: List[Dict[str, Any]], algo: str) -> List[float]:
    vals = []
    for r in results:
        s = r["scores"].get(algo)
        if s is not None:
            vals.append(float(s))
    return vals

def _stats(vals: List[float]) -> Dict[str, Any]:
    if not vals:
        return {"n": 0, "min": None, "max": None, "mean": None, "median": None}
    return {
        "n": len(vals),
        "min": min(vals),
        "max": max(vals),
        "mean": sum(vals) / len(vals),
        "median": stats.median(vals),
    }

def _bucket_counts(vals: List[float]) -> Dict[str, int]:
    # buckets por similitud (cos/sbert/jaccard ~ [0,1])
    buckets = {
        "≥0.80": 0,
        "0.60–0.79": 0,
        "0.40–0.59": 0,
        "0.20–0.39": 0,
        "<0.20": 0,
    }
    for v in vals:
        if v >= 0.80: buckets["≥0.80"] += 1
        elif v >= 0.60: buckets["0.60–0.79"] += 1
        elif v >= 0.40: buckets["0.40–0.59"] += 1
        elif v >= 0.20: buckets["0.20–0.39"] += 1
        else: buckets["<0.20"] += 1
    return buckets

def _rank(results: List[Dict[str, Any]], algo: str, top: int) -> List[Dict[str, Any]]:
    ranked = sorted(
        results,
        key=lambda r: (r["scores"].get(algo) or 0.0),
        reverse=True
    )
    return ranked[:top]

def _safe_get(d: Dict[str, Any], *keys, default: str = "") -> str:
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return str(cur)

def generate_markdown(data: Dict[str, Any], algo: str, top: int, out_md: Path):
    """
    Genera reporte completo de similitud en formato Markdown.
    
    Crea documento Markdown con:
    - Encabezado y contexto
    - Selección de artículos
    - Estadísticas descriptivas
    - Distribución por rangos
    - Top N pares más similares
    - Comparación multi-algoritmo
    - Apéndice explicativo
    
    Args:
        data (Dict[str, Any]): Diccionario con resultados completos
        algo (str): Nombre del algoritmo principal
        top (int): Cantidad de top pares a incluir
        out_md (Path): Ruta del archivo Markdown de salida
    
    Output estructura:
        # Reporte de Similitud Textual
        **Algoritmo principal:** ...
        
        ## Selección de artículos
        ## Estadísticas generales
        ## Distribución por rangos
        ## Top N pares por <algoritmo>
        ## Comparación de algoritmos
        ## Apéndice — ¿Cómo se calculan las similitudes?
    
    Notas:
        - Crea directorio de salida si no existe
        - Sobrescribe archivo existente
        - Formato compatible con GitHub, Jupyter, pandoc
    """
    selected = data.get("selected", [])
    results = data.get("results", [])

    vals = _flat_scores_for_algo(results, algo)
    s = _stats(vals)
    buckets = _bucket_counts(vals)
    ranked = _rank(results, algo, min(top, len(results)))

    # Encabezado y contexto
    md = []
    md.append("# Reporte de Similitud Textual")
    md.append("")
    md.append(f"**Algoritmo principal:** {algo}")
    md.append(f"**Pares totales:** {len(results)}")
    md.append("")
    md.append("## Selección de artículos")
    for item in selected:
        md.append(f"- [{item['index']}] {item.get('title','').strip()}")
    md.append("")

    # Resumen estadístico
    md.append("## Estadísticas generales")
    md.append("")
    md.append("| Métrica | Valor |")
    md.append("|---|---:|")
    md.append(f"| n | {s['n']} |")
    md.append(f"| min | {_pct(s['min']) if s['min'] is not None else '—'} |")
    md.append(f"| max | {_pct(s['max']) if s['max'] is not None else '—'} |")
    md.append(f"| media | {_pct(s['mean']) if s['mean'] is not None else '—'} |")
    md.append(f"| mediana | {_pct(s['median']) if s['median'] is not None else '—'} |")
    md.append("")

    md.append("### Distribución por rangos")
    md.append("")
    md.append("| Rango | Conteo |")
    md.append("|---|---:|")
    for k, v in buckets.items():
        md.append(f"| {k} | {v} |")
    md.append("")

    # Top pares por algoritmo principal
    md.append(f"## Top {len(ranked)} pares por {algo} (Algoritmo Principal)")
    md.append("")
    md.append("| Rank | Índices (i,j) | % Similitud | Título i | Título j |")
    md.append("|---:|:---:|---:|---|---|")
    for idx, r in enumerate(ranked, 1):
        score = r["scores"].get(algo)
        md.append(
            f"| {idx} | {r['i']},{r['j']} | {_pct(score)} | "
            f"{_safe_get(r, 'title_i').strip()} | {_safe_get(r, 'title_j').strip()} |"
        )
    md.append("")

    # Tabla comparativa por algoritmo (COMPLETA - todos los pares)
    md.append("## Comparación de los 6 Algoritmos")
    md.append("")
    md.append("### Todos los pares comparados")
    md.append("")
    
    # Detectar todos los algoritmos presentes (unión de claves)
    algos_all = []
    for r in results:
        for k in r.get("scores", {}).keys():
            if k not in algos_all:
                algos_all.append(k)
    
    # Ordenar algoritmos: primero clásicos, luego IA
    classic_order = ["Levenshtein (normalizada)", "Damerau–Levenshtein (normalizada)", "Jaccard (tokens)", "Coseno (TF-IDF)"]
    ai_order = ["SBERT (coseno)", "GTE (coseno)"]
    algos_sorted = [a for a in classic_order if a in algos_all] + [a for a in ai_order if a in algos_all]
    
    md.append("**Algoritmos Clásicos (4):**")
    md.append("- **Levenshtein**: Distancia de edición (inserción, eliminación, sustitución)")
    md.append("- **Damerau-Levenshtein**: Levenshtein + transposición de caracteres adyacentes")
    md.append("- **Jaccard**: Similitud de conjuntos de tokens (intersección / unión)")
    md.append("- **Coseno TF-IDF**: Vectorización estadística con pesos TF-IDF")
    md.append("")
    md.append("**Algoritmos con IA (2):**")
    md.append("- **SBERT**: Sentence-BERT embeddings (all-MiniLM-L6-v2)")
    md.append("- **GTE**: General Text Embeddings (thenlper/gte-small)")
    md.append("")
    
    md.append("| Par (i,j) | " + " | ".join(algos_sorted) + " |")
    md.append("|:--:|" + "|".join([":--:" for _ in algos_sorted]) + "|")
    
    # Ordenar resultados por el algoritmo principal para mejor visualización
    results_sorted = sorted(results, key=lambda r: r["scores"].get(algo, 0), reverse=True)
    
    for r in results_sorted:
        row = [f"({r['i']},{r['j']})"]
        for a in algos_sorted:
            score_val = r["scores"].get(a)
            row.append(_pct(score_val))
        md.append("| " + " | ".join(row) + " |")
    md.append("")
    
    # Estadísticas por algoritmo
    md.append("### Estadísticas por Algoritmo")
    md.append("")
    md.append("| Algoritmo | Media | Mediana | Min | Max |")
    md.append("|---|:--:|:--:|:--:|:--:|")
    
    for a in algos_sorted:
        vals_a = _flat_scores_for_algo(results, a)
        stats_a = _stats(vals_a)
        md.append(f"| {a} | {_pct(stats_a['mean'])} | {_pct(stats_a['median'])} | {_pct(stats_a['min'])} | {_pct(stats_a['max'])} |")
    md.append("")
    
    # Análisis de divergencias
    md.append("### Análisis de Divergencias entre Algoritmos")
    md.append("")
    md.append("Los algoritmos **clásicos** (basados en caracteres y tokens) suelen dar scores **bajos** porque:")
    md.append("- Solo detectan coincidencias exactas de palabras")
    md.append("- No capturan similitud semántica (sinónimos, paráfrasis)")
    md.append("- Son sensibles a diferencias de redacción")
    md.append("")
    md.append("Los algoritmos **con IA** (SBERT, GTE) dan scores **más altos** porque:")
    md.append("- Capturan significado semántico de los textos")
    md.append("- Detectan similitud conceptual aunque las palabras sean diferentes")
    md.append("- Están entrenados en millones de textos para aprender relaciones semánticas")
    md.append("")
    
    # Ranking individual para cada algoritmo
    md.append("## Ranking por Algoritmo Individual")
    md.append("")
    md.append("A continuación se muestra el ranking de los pares según cada uno de los 6 algoritmos:")
    md.append("")
    
    for a in algos_sorted:
        md.append(f"### {a}")
        md.append("")
        
        # Ordenar resultados por este algoritmo específico
        ranked_by_algo = sorted(results, key=lambda r: r["scores"].get(a, 0), reverse=True)
        
        md.append("| Rank | Par (i,j) | Similitud | Título i | Título j |")
        md.append("|---:|:---:|---:|---|---|")
        
        for idx, r in enumerate(ranked_by_algo, 1):
            score = r["scores"].get(a)
            md.append(
                f"| {idx} | ({r['i']},{r['j']}) | {_pct(score)} | "
                f"{_safe_get(r, 'title_i').strip()} | {_safe_get(r, 'title_j').strip()} |"
            )
        md.append("")
    
    md.append(appendix_markdown())
    
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md), encoding="utf-8")

def generate_csv_top(data: Dict[str, Any], algo: str, top: int, out_csv: Path):
    """
    Genera archivo CSV con top N pares más similares.
    
    Exporta tabla con ranking de pares para análisis externo
    en Excel, R, Python, etc.
    
    Args:
        data (Dict[str, Any]): Diccionario con resultados completos
        algo (str): Nombre del algoritmo para ordenar
        top (int): Cantidad de pares a incluir
        out_csv (Path): Ruta del archivo CSV de salida
    
    Columnas CSV:
        - rank: Posición en ranking (1-based)
        - i: Índice del primer artículo
        - j: Índice del segundo artículo
        - score: Score de similitud (6 decimales)
        - score_pct: Score como porcentaje formateado
        - title_i: Título del artículo i
        - title_j: Título del artículo j
    
    Example row:
        1,0,5,0.856234,85.6%,"Machine Learning Models","Deep Learning..."
    
    Notas:
        - Crea directorio si no existe
        - Encoding UTF-8 para caracteres especiales
        - Headers incluidos en primera línea
        - Formato estándar RFC 4180
    """
    results = data.get("results", [])
    ranked = _rank(results, algo, min(top, len(results)))
    # columnas
    fieldnames = ["rank", "i", "j", "score", "score_pct", "title_i", "title_j"]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for idx, r in enumerate(ranked, 1):
            s = r["scores"].get(algo)
            w.writerow({
                "rank": idx,
                "i": r["i"],
                "j": r["j"],
                "score": f"{s:.6f}" if s is not None else "",
                "score_pct": _pct(s),
                "title_i": _safe_get(r, "title_i"),
                "title_j": _safe_get(r, "title_j"),
            })

def print_console_summary(data: Dict[str, Any], algo: str, top: int):
    """
    Imprime resumen de resultados en consola de forma legible.
    
    Args:
        data (Dict[str, Any]): Diccionario con resultados completos
        algo (str): Nombre del algoritmo principal
        top (int): Cantidad de top pares a mostrar
    
    Output:
        === Resumen de Similitud ===
        Algoritmo principal: <nombre>
        Artículos seleccionados: [índices]
        Pares: N | media=X% mediana=X% min=X% max=X%
        
        Top N pares por <algoritmo>:
        1. (i,j) XX.X% | título_i... <> título_j...
        ...
    
    Notas:
        - Títulos truncados a 60 caracteres para legibilidad
        - Formato compacto para revisión rápida
        - Complementa reporte Markdown con vista previa
    """
    results = data.get("results", [])
    selected = data.get("selected", [])
    vals = _flat_scores_for_algo(results, algo)
    s = _stats(vals)
    print("\n=== Resumen de Similitud ===")
    print(f"Algoritmo principal: {algo}")
    print(f"Artículos seleccionados: {[it['index'] for it in selected]}")
    print(f"Pares: {len(results)}  |  media={_pct(s['mean']) if s['mean'] is not None else '—'}  "
          f"mediana={_pct(s['median']) if s['median'] is not None else '—'}  "
          f"min={_pct(s['min']) if s['min'] is not None else '—'}  max={_pct(s['max']) if s['max'] is not None else '—'}")

    ranked = _rank(results, algo, min(top, len(results)))
    print(f"\nTop {len(ranked)} pares por {algo}:")
    for idx, r in enumerate(ranked, 1):
        s = r["scores"].get(algo)
        print(f"{idx:>2}. ({r['i']},{r['j']})  {_pct(s)}  |  {r['title_i'][:60]}  <>  {r['title_j'][:60]}")

def main():
    """
    Función principal para generación de reportes desde línea de comandos.
    
    Coordina generación de reportes en múltiples formatos (Markdown, CSV, consola)
    a partir de resultados de análisis de similitud.
    
    Argumentos CLI:
        --json: Ruta al JSON de resultados (default: data/processed/similitud_req2.json)
        --md: Ruta de salida Markdown (default: data/processed/reporte_similitud.md)
        --csv: Ruta de salida CSV (default: data/processed/reporte_similitud_top.csv)
        --top: Cantidad de top pares (default: 10)
        --algo: Algoritmo principal (default: auto-selección)
    
    Pipeline:
        1. Lee JSON de resultados
        2. Valida presencia de pares
        3. Detecta/selecciona algoritmo principal
        4. Imprime resumen en consola
        5. Genera reporte Markdown completo
        6. Genera tabla CSV de top pares
        7. Reporta archivos generados
    
    Example:
        $ python reports.py --algo "GTE (coseno)" --top 15
        $ python reports.py --json custom.json --md custom.md
        $ python reports.py  # usa todos los defaults
    
    Output:
        - Resumen en consola inmediato
        - Archivo Markdown comprehensivo
        - Archivo CSV para análisis externo
        - Mensaje de confirmación con rutas
    
    Raises:
        FileNotFoundError: Si JSON de entrada no existe
        ValueError: Si JSON no contiene resultados válidos
    
    Notas:
        - Todos los argumentos opcionales con defaults razonables
        - Crea directorios de salida automáticamente
        - Sobrescribe archivos existentes
        - Compatible con pipelines automatizados
    """
    p = argparse.ArgumentParser(description="Genera reporte legible de similitud (porcentajes, ranking y estadísticas).")
    p.add_argument("--json", type=str, default=str(DEFAULT_JSON), help="Ruta al similitud_req2.json")
    p.add_argument("--md", type=str, default=str(DEFAULT_MD), help="Ruta de salida Markdown")
    p.add_argument("--csv", type=str, default=str(DEFAULT_CSV), help="Ruta de salida CSV TOP")
    p.add_argument("--top", type=int, default=10, help="Cantidad de pares a mostrar")
    p.add_argument("--algo", type=str, default=None, help="Algoritmo principal (si omites, se elige automáticamente)")
    args = p.parse_args()

    data = _read_json(Path(args.json))
    results = data.get("results", [])
    if not results:
        raise ValueError("El JSON no contiene pares en 'results'.")

    algo = _detect_primary_algo(results, args.algo)
    print_console_summary(data, algo, args.top)
    generate_markdown(data, algo, args.top, Path(args.md))
    generate_csv_top(data, algo, args.top, Path(args.csv))
    print(f"\nArchivos generados:\n- {args.md}\n- {args.csv}")

if __name__ == "__main__":
    main()
