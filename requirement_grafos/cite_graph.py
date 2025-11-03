"""
Módulo para construcción de grafos de citaciones dirigidos.

Este módulo genera grafos que representan relaciones de citación entre artículos
científicos basándose en similitud temática y temporalidad, dado que los datos
BibTeX no incluyen referencias explícitas.
"""
from __future__ import annotations
from typing import Dict, List, Any, Tuple
from pathlib import Path
import math

import pandas as pd

from requirement_3.data_loader import load_bib_dataframe, DEFAULT_BIB
from requirement_2.preprocessing import Preprocessor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Instancia global del preprocesador de texto
pp = Preprocessor()

def _int_year(y: Any) -> int | None:
    """
    Extrae y valida el año de publicación de un campo BibTeX.
    
    Args:
        y: Campo de año que puede ser int, str o None
        
    Returns:
        int | None: Año como entero si es válido (entre 1800-2100), None en caso contrario
        
    Examples:
        >>> _int_year("2024")
        2024
        >>> _int_year("2024-05")
        2024
        >>> _int_year("invalid")
        None
    """
    try:
        # Extrae los primeros 4 caracteres y los convierte a entero
        i = int(str(y)[:4])
        # Valida que esté en un rango razonable para publicaciones científicas
        if 1800 <= i <= 2100: 
            return i
    except Exception:
        return None
    return None

def build_citation_graph(
    bib_path: Path = DEFAULT_BIB,
    min_sim: float = 0.35,
    use_explicit: bool = True
) -> Dict[str, Any]:
    """
    Construye un grafo dirigido de citaciones basado en similitud temática entre artículos.
    
    Como los archivos BibTeX de ACM no incluyen referencias explícitas, este método
    infiere relaciones de citación utilizando:
    1. Similitud TF-IDF entre metadatos (título, keywords, autores)
    2. Dirección temporal: artículos más recientes "citan" a los más antiguos
    3. En ausencia de año, usa el orden en el dataset
    
    Args:
        bib_path (Path): Ruta al archivo BibTeX con los artículos
        min_sim (float): Umbral mínimo de similitud para crear una arista (0.0-1.0)
        use_explicit (bool): Parámetro reservado para futuras implementaciones con 
                            referencias explícitas (actualmente no se usa)
    
    Returns:
        Dict[str, Any]: Diccionario con tres claves:
            - 'nodes': Lista de nodos, cada uno con {id, title, year, journal}
            - 'edges': Lista de aristas dirigidas {u, v, w} donde u→v con peso w (similitud)
            - 'adj': Diccionario de adyacencia {u: {v: costo}} donde costo = 1-similitud
    
    Estructura del grafo retornado:
        {
            'nodes': [
                {'id': 'A0', 'title': '...', 'year': 2024, 'journal': '...'},
                {'id': 'A1', 'title': '...', 'year': 2023, 'journal': '...'},
                ...
            ],
            'edges': [
                {'u': 'A0', 'v': 'A1', 'w': 0.6534},  # A0 cita a A1 con similitud 0.6534
                ...
            ],
            'adj': {
                'A0': {'A1': 0.3466, 'A5': 0.4123},  # costos para algoritmos de caminos
                ...
            }
        }
    
    Notas:
        - Los IDs de nodos son 'A0', 'A1', ..., 'An' según el orden en el BibTeX
        - El peso 'w' en edges representa similitud (mayor = más similar)
        - El peso en 'adj' representa costo (menor = más cercano) para algoritmos
        - No se crean aristas duplicadas entre el mismo par de nodos
        - La dirección siempre va del documento más nuevo al más antiguo
    """
    # Cargar datos bibliográficos desde el archivo BibTeX
    df = load_bib_dataframe(bib_path)
    
    # === PASO 1: Preparar textos para cálculo de similitud ===
    # Concatena título, keywords y autores de cada artículo
    cols = ["title", "keywords", "authors"]
    texts = []
    for i, r in df.iterrows():
        # Combina los campos en un solo string
        chunk = " ".join(str(r.get(c, "")) for c in cols)
        # Limpia y normaliza el texto (lowercasing, stopwords, etc.)
        texts.append(pp.clean(chunk))

    # === PASO 2: Calcular matriz de similitud TF-IDF ===
    # Vectoriza los textos usando TF-IDF (Term Frequency - Inverse Document Frequency)
    vec = TfidfVectorizer()
    X = vec.fit_transform(texts)
    # Calcula similitud coseno entre todos los pares de documentos
    # Resultado: matriz S[i,j] = similitud entre documento i y j (0.0 a 1.0)
    S = cosine_similarity(X)
    
    # === PASO 3: Crear nodos del grafo ===
    n = len(df)
    nodes = []
    for i in range(n):
        # Cada nodo representa un artículo con su metadata
        nodes.append({
            "id": f"A{i}",  # Identificador único del artículo
            "title": str(df.iloc[i].get("title", "")),
            "year": _int_year(df.iloc[i].get("year", "")),  # Año validado
            "journal": str(df.iloc[i].get("journal", "")),
        })

    # === PASO 4: Crear aristas dirigidas basadas en similitud y temporalidad ===
    edges = []
    # Diccionario de adyacencia: adj[u][v] = costo del camino u→v
    adj: Dict[str, Dict[str, float]] = {f"A{i}": {} for i in range(n)}

    # Inferencia de aristas: compara cada par de artículos
    for i in range(n):
        for j in range(n):
            if i == j: 
                continue  # No crear auto-aristas
            
            sim = float(S[i, j])  # Similitud entre artículos i y j
            
            if sim >= min_sim:  # Solo crear arista si supera el umbral
                ai, aj = nodes[i], nodes[j]
                yi, yj = ai["year"], aj["year"]
                
                # Determinar dirección de la arista según temporalidad
                if yi is not None and yj is not None and yi != yj:
                    # Regla: artículo más nuevo → artículo más antiguo
                    # (asume que el nuevo cita al antiguo)
                    u, v = (f"A{i}", f"A{j}") if yi > yj else (f"A{j}", f"A{i}")
                else:
                    # Sin información de año: usar orden en dataset
                    # (índice mayor → índice menor)
                    u, v = (f"A{i}", f"A{j}") if i > j else (f"A{j}", f"A{i}")
                
                # Pesos de la arista:
                w_sim = sim  # Peso de similitud (mayor = más similar)
                w_cost = 1.0 - w_sim  # Costo (menor = más cercano, para Dijkstra)
                
                # Evitar aristas duplicadas u→v
                if v not in adj[u]:
                    edges.append({"u": u, "v": v, "w": round(w_sim, 4)})
                    adj[u][v] = round(w_cost, 6)

    return {"nodes": nodes, "edges": edges, "adj": adj}
