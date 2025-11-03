"""
Módulo de explicaciones pedagógicas de algoritmos de similitud.

Provee descripciones paso a paso y documentación educativa de cómo
funcionan los algoritmos de similitud implementados en el proyecto.

Funcionalidades:
- Explicaciones en texto plano de cada algoritmo
- Generación de apéndice Markdown para reportes
- Descripciones de fórmulas y procesos

Parte del Requerimiento 2: Documentación y explicación de algoritmos.
"""
# requirement_2/explainers.py
from __future__ import annotations
from typing import Dict, List

def algorithm_explanations() -> Dict[str, List[str]]:
    """
    Retorna explicaciones paso a paso de algoritmos de similitud.
    
    Provee descripciones educativas en texto plano de cómo cada algoritmo
    calcula similitud, sus fórmulas principales y características clave.
    
    Returns:
        Dict[str, List[str]]: Diccionario {nombre_algoritmo: [pasos]}
                             Cada lista contiene strings con pasos del proceso
    
    Algoritmos explicados:
        - Levenshtein (normalizada)
        - Damerau–Levenshtein (normalizada)
        - Jaccard (tokens)
        - Coseno (TF-IDF)
        - SBERT (coseno)
        - GTE (coseno)
    
    Example:
        >>> expl = algorithm_explanations()
        >>> for step in expl["Jaccard (tokens)"]:
        ...     print(step)
        Convierte cada texto a un conjunto de palabras (tokens)...
        Calcula |A∩B|/|A∪B| en [0,1]...
        Mide traslape del vocabulario...
    
    Notas:
        - Explicaciones orientadas a usuarios no técnicos
        - Cada paso es autocontenido y comprensible
        - Útil para reportes, documentación y educación
        - Se usa en appendix_markdown() para reportes
    """
    return {
        "Levenshtein (normalizada)": [
            "Mide la distancia de edición mínima entre dos textos (insertar, borrar, sustituir).",
            "Se usa programación dinámica con una matriz dp de tamaño (m+1)x(n+1).",
            "La similitud se normaliza: sim = 1 - dist/max(|a|,|b|)."
        ],
        "Damerau–Levenshtein (normalizada)": [
            "Extiende Levenshtein añadiendo la operación de transposición (intercambio de adyacentes).",
            "Usa DP y compara también dp[i-2][j-2] + 1 cuando hay transposición.",
            "Se normaliza igual: sim = 1 - dist/max(|a|,|b|)."
        ],
        "Jaccard (tokens)": [
            "Convierte cada texto a un conjunto de palabras (tokens) sin repeticiones.",
            "Calcula |A∩B|/|A∪B| en [0,1].",
            "Mide traslape del vocabulario, sin considerar orden ni frecuencia."
        ],
        "Coseno (TF-IDF)": [
            "Construye vectores TF-IDF por documento: v_d[t] = tf_d(t)*idf(t).",
            "idf(t) ≈ log((N+1)/(df(t)+1)) + 1; TF es frecuencia relativa.",
            "La similitud es el coseno entre vectores (x·y)/(||x||·||y||)."
        ],
        "SBERT (coseno)": [
            "Cada texto se transforma en un embedding (vector) con Sentence-BERT.",
            "Se normaliza el vector y se aplica coseno entre embeddings.",
            "Captura similitud semántica (sinónimos/paráfrasis)."
        ],
        "GTE (coseno)": [
            "Modelo de embeddings reciente (thenlper/gte-small).",
            "Convierte cada texto en un embedding; similitud por coseno.",
            "Gratis y rápido; buen desempeño semántico."
        ],
    }

def appendix_markdown() -> str:
    """
    Genera apéndice Markdown con explicaciones de todos los algoritmos.
    
    Construye sección de documentación formateada en Markdown explicando
    cómo funciona cada algoritmo de similitud implementado.
    
    Returns:
        str: Texto Markdown con sección "## Apéndice" completa
    
    Estructura del output:
        ## Apéndice — ¿Cómo se calculan las similitudes?
        
        ### Levenshtein (normalizada)
        - paso 1
        - paso 2
        ...
        
        ### Damerau–Levenshtein (normalizada)
        - paso 1
        ...
    
    Example:
        >>> md = appendix_markdown()
        >>> print(md[:100])
        ## Apéndice — ¿Cómo se calculan las similitudes?
        
        ### Levenshtein (normalizada)...
    
    Uso:
        Se incluye al final de reportes Markdown generados por reports.py
        para proveer contexto educativo sobre los algoritmos usados.
    
    Notas:
        - Orden de algoritmos predefinido (clásicos primero, IA después)
        - Formato Markdown compatible con GitHub, Jupyter, HTML
        - Bullets (−) para pasos individuales
        - Líneas en blanco entre secciones para legibilidad
    """
    parts = []
    parts.append("## Apéndice — ¿Cómo se calculan las similitudes?\n")
    expl = algorithm_explanations()
    order = [
        "Levenshtein (normalizada)",
        "Damerau–Levenshtein (normalizada)",
        "Jaccard (tokens)",
        "Coseno (TF-IDF)",
        "SBERT (coseno)",
        "GTE (coseno)",
    ]
    for name in order:
        if name in expl:
            parts.append(f"### {name}\n")
            for step in expl[name]:
                parts.append(f"- {step}")
            parts.append("")  # línea en blanco
    return "\n".join(parts)
