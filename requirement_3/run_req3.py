"""
Script principal del Requerimiento 3: Análisis de frecuencia y extracción automática de términos.

Funcionalidades:
- Carga de corpus bibliográfico desde archivo .bib
- Análisis de frecuencia de términos semilla (ground truth)
- Extracción automática de términos relevantes usando TF-IDF
- Evaluación de calidad de términos auto-generados vs semilla
- Generación de reporte JSON con resultados completos
- Resumen en consola con métricas clave

Pipeline completo:
    1. Cargar y procesar archivo BibTeX
    2. Calcular frecuencias de términos semilla por documento y globales
    3. Extraer términos automáticamente con TF-IDF
    4. Calcular frecuencias de términos auto-generados
    5. Evaluar precisión semántica usando embeddings
    6. Exportar resultados a JSON
    7. Mostrar resumen en consola

Parte del Requerimiento 3: Análisis bibliométrico de términos.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse

from requirement_3.data_loader import load_bib_dataframe, DEFAULT_BIB, PROJECT_ROOT
from requirement_3.frequency import normalize_terms, term_frequencies_per_doc, aggregate_frequencies
from requirement_3.auto_terms import extract_auto_terms
from requirement_3.evaluate import precision_against_seeds
from requirement_3.keywords import CATEGORY_NAME, SEED_WORDS

OUT_JSON = PROJECT_ROOT / "requirement_3" / "req3_resultados.json"

def run_req3(
    bib_path: Path = DEFAULT_BIB,
    max_auto_terms: int = 15,
    min_df: int = 2,
    threshold: float = 0.50
) -> str:
    """
    Ejecuta pipeline completo de análisis de frecuencia y extracción de términos.
    
    Coordina todas las etapas del requerimiento 3: carga de datos, análisis de
    frecuencias de términos semilla, extracción automática de términos con TF-IDF,
    y evaluación de calidad usando similitud semántica.
    
    Args:
        bib_path (Path, optional): Ruta al archivo .bib. 
                                   Default: data/processed/productos_unificados.bib
        max_auto_terms (int, optional): Máximo términos a extraer automáticamente. Default: 15
        min_df (int, optional): Frecuencia mínima de documento para términos. Default: 2
        threshold (float, optional): Umbral similitud semántica [0,1]. Default: 0.50
    
    Returns:
        str: Ruta al archivo JSON con resultados generado
    
    Pipeline:
        1. Cargar DataFrame desde .bib con load_bib_dataframe()
        2. Extraer lista de abstracts del DataFrame
        3. Normalizar SEED_WORDS con normalize_terms()
        4. Calcular frecuencias de semillas:
           - Por documento con term_frequencies_per_doc()
           - Agregadas con aggregate_frequencies()
        5. Extraer términos automáticos con extract_auto_terms()
        6. Calcular frecuencias de términos auto-generados
        7. Evaluar precisión con precision_against_seeds()
        8. Construir payload JSON con todos los resultados
        9. Guardar en requirement_3/req3_resultados.json
        10. Retornar ruta del archivo
    
    Estructura JSON output:
        {
            "category": str,
            "seed_words_original": List[str],
            "seed_words_normalized": List[str],
            "freq_per_doc_seeds": List[Dict[str, int]],
            "freq_total_seeds": Dict[str, int],
            "auto_terms": List[str],
            "freq_per_doc_auto": List[Dict[str, int]],
            "freq_total_auto": Dict[str, int],
            "evaluation": {
                "model": str,
                "threshold": float,
                "precision": float,
                "details": List[Dict]
            },
            "params": Dict,
            "counts": Dict
        }
    
    Example:
        >>> result = run_req3(max_auto_terms=20, threshold=0.70)
        >>> print(result)
        '/path/to/requirement_3/req3_resultados.json'
    
    Raises:
        FileNotFoundError: Si el archivo .bib no existe
        ValueError: Si el .bib no contiene entradas válidas
    
    Notas:
        - Crea directorio requirement_3 si no existe
        - Sobrescribe req3_resultados.json en cada ejecución
        - Todos los parámetros son configurables vía argumentos
        - min_df filtra términos que aparecen en < min_df documentos
        - threshold controla strictness de evaluación semántica
    """
    df = load_bib_dataframe(bib_path)
    abstracts = [str(x) for x in df["abstract"].tolist()]
    # 1) Frecuencias de SEED_WORDS
    seeds_norm = normalize_terms(SEED_WORDS)
    per_doc = term_frequencies_per_doc(abstracts, seeds_norm)
    agg = aggregate_frequencies(per_doc)

    # 2) Términos auto-generados (máx. 15) por TF-IDF
    auto_terms = extract_auto_terms(abstracts, max_terms=max_auto_terms, min_df=min_df)

    # 3) Frecuencia de términos auto-generados
    auto_per_doc = term_frequencies_per_doc(abstracts, auto_terms)
    auto_agg = aggregate_frequencies(auto_per_doc)

    # 4) Precisión de términos auto-generados vs. semillas (embeddings)
    eval_res = precision_against_seeds(auto_terms, seeds_norm, threshold=threshold)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "category": CATEGORY_NAME,
        "seed_words_original": SEED_WORDS,
        "seed_words_normalized": seeds_norm,
        "freq_per_doc_seeds": per_doc,
        "freq_total_seeds": agg,
        "auto_terms": auto_terms,
        "freq_per_doc_auto": auto_per_doc,
        "freq_total_auto": auto_agg,
        "evaluation": eval_res,
        "params": {"max_auto_terms": max_auto_terms, "min_df": min_df, "threshold": threshold},
        "counts": {"num_documents": len(abstracts)}
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(OUT_JSON)

def _pct(x: float) -> str:
    """
    Formatea número decimal como porcentaje con 1 decimal.
    
    Args:
        x (float): Valor decimal [0,1] o None
    
    Returns:
        str: Porcentaje formateado "X.X%" o "—" si None
    
    Example:
        >>> _pct(0.8567)
        '85.7%'
        >>> _pct(None)
        '—'
    """
    return f"{x*100:,.1f}%" if x is not None else "—"

def print_console_summary(json_path: Path):
    """
    Imprime resumen formateado de resultados del requerimiento 3 en consola.
    
    Lee archivo JSON de resultados y genera reporte legible con:
    - Información de categoría y corpus
    - Frecuencias de términos semilla
    - Términos auto-generados y sus frecuencias
    - Métricas de evaluación con detalle por término
    
    Args:
        json_path (Path): Ruta al archivo JSON con resultados
    
    Output en consola:
        ================ Requerimiento 3 — Resumen ================
        Categoría: <category>
        Documentos (abstracts): <count>
        -----------------------------------------------------------
        Frecuencias globales (palabras asociadas provistas):
          - término_1                  frecuencia
          - término_2                  frecuencia
        -----------------------------------------------------------
        Términos auto-generados (top) y frecuencias:
          - término_1                  frecuencia
          - término_2                  frecuencia
        -----------------------------------------------------------
        Evaluación de precisión de nuevos términos (embeddings):
          Modelo: <model>  |  Umbral: <threshold>
          Precisión: <precision>
           ✔ término_relevante         sim=0.XXX
           ✖ término_no_relevante      sim=0.XXX
        ===========================================================
    
    Símbolos:
        ✔ : Término relevante (similitud >= umbral)
        ✖ : Término no relevante (similitud < umbral)
    
    Notas:
        - Formatea porcentajes con 1 decimal
        - Alinea términos en columnas para legibilidad
        - Usa símbolos Unicode para indicación visual
        - Muestra detalle completo de evaluación
    """
    import json
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    seeds = data["seed_words_normalized"]
    agg = data["freq_total_seeds"]
    auto = data["auto_terms"]
    auto_agg = data["freq_total_auto"]
    eval_res = data["evaluation"]

    print("\n================ Requerimiento 3 — Resumen ================")
    print(f"Categoría: {data['category']}")
    print(f"Documentos (abstracts): {data['counts']['num_documents']}")
    print("-----------------------------------------------------------")
    print("Frecuencias globales (palabras asociadas provistas):")
    for s in seeds:
        print(f"  - {s:25s}  {agg.get(s, 0)}")
    print("-----------------------------------------------------------")
    print("Términos auto-generados (top) y frecuencias:")
    for t in auto:
        print(f"  - {t:25s}  {auto_agg.get(t, 0)}")
    print("-----------------------------------------------------------")
    print("Evaluación de precisión de nuevos términos (embeddings):")
    print(f"  Modelo: {eval_res['model']}  |  Umbral: {_pct(eval_res['threshold'])}")
    print(f"  Precisión: {_pct(eval_res['precision'])}")
    for d in eval_res["details"]:
        flag = "✔" if d["relevant"] else "✖"
        print(f"   {flag} {d['term']:25s}  sim={d['max_sim']:.3f}")
    print("===========================================================\n")

def main():
    """
    Función principal ejecutada al correr el script desde línea de comandos.
    
    Parsea argumentos CLI, ejecuta pipeline completo del requerimiento 3,
    y muestra resultados en consola.
    
    Argumentos CLI:
        --bib: Ruta al archivo .bib (default: data/processed/productos_unificados.bib)
        --max-terms: Máximo de términos a extraer automáticamente (default: 15)
        --min-df: Frecuencia mínima de documento para términos (default: 2)
        --thr: Umbral de similitud semántica [0,1] (default: 0.50)
    
    Example:
        $ python run_req3.py --max-terms 20 --thr 0.70
        $ python run_req3.py --bib custom.bib --min-df 3
        $ python run_req3.py  # usa todos los defaults
    
    Output:
        - Archivo JSON: requirement_3/req3_resultados.json
        - Resumen formateado en consola con métricas clave
    
    Notas:
        - Todos los argumentos son opcionales con defaults razonables
        - min-df de 2 filtra términos muy raros
        - threshold de 0.50 es balanceado (ni muy permisivo ni estricto)
        - max-terms de 15 provee lista manejable sin redundancia
    """
    ap = argparse.ArgumentParser(description="Requerimiento 3: Frecuencia de términos + auto términos + evaluación.")
    ap.add_argument("--bib", type=str, default=str(DEFAULT_BIB), help="Ruta al .bib (por defecto data/processed/productos_unificados.bib)")
    ap.add_argument("--max-terms", type=int, default=15, help="Máximo de términos auto-generados")
    ap.add_argument("--min-df", type=int, default=2, help="Mínimo documentos donde debe aparecer un término")
    ap.add_argument("--thr", type=float, default=0.50, help="Umbral de similitud (embeddings) para marcar relevancia")
    args = ap.parse_args()

    out = run_req3(bib_path=Path(args.bib), max_auto_terms=args.max_terms, min_df=args.min_df, threshold=args.thr)
    print(f"OK. Archivo generado: {out}")
    print_console_summary(Path(out))

if __name__ == "__main__":
    main()
