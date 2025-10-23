# requirement_2/explainers.py
from __future__ import annotations
from typing import Dict, List

def algorithm_explanations() -> Dict[str, List[str]]:
    """Devuelve explicaciones paso a paso por algoritmo (texto simple)."""
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
    """Bloque Markdown con la explicación completa (resumen amigable)."""
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
