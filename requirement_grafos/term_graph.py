"""
Módulo para construcción de grafos de co-ocurrencia de términos no dirigidos.

Este módulo genera grafos que representan relaciones entre términos técnicos
basándose en su co-ocurrencia dentro de ventanas de texto en los abstracts.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any, Iterable
from pathlib import Path
from collections import defaultdict, Counter
import itertools

import pandas as pd

from requirement_3.data_loader import load_bib_dataframe, DEFAULT_BIB
from requirement_2.preprocessing import Preprocessor

# Instancia global del preprocesador de texto
pp = Preprocessor()

def _window_cooccurrence(tokens: List[str], vocab: set[str], window: int = 20) -> Counter[Tuple[str,str]]:
    """
    Calcula co-ocurrencias de términos dentro de ventanas deslizantes de texto.
    
    Utiliza una ventana deslizante sobre la secuencia de tokens para identificar
    pares de términos que aparecen cerca uno del otro. Solo cuenta pares donde
    ambos términos están en el vocabulario especificado.
    
    Args:
        tokens (List[str]): Secuencia de tokens del texto (ya tokenizado)
        vocab (set[str]): Conjunto de términos de interés para contar co-ocurrencias
        window (int): Tamaño de la ventana en tokens (por defecto 20)
        
    Returns:
        Counter[Tuple[str,str]]: Contador de pares ordenados (term1, term2) con 
                                sus frecuencias de co-ocurrencia
    
    Ejemplo:
        >>> tokens = ["machine", "learning", "is", "a", "type", "of", "artificial", "intelligence"]
        >>> vocab = {"machine", "learning", "artificial", "intelligence"}
        >>> result = _window_cooccurrence(tokens, vocab, window=10)
        >>> result[("artificial", "machine")]  # Ordenado alfabéticamente
        1
        
    Notas:
        - Los pares se almacenan en orden alfabético para evitar duplicados
        - No se cuentan auto-co-ocurrencias (término consigo mismo)
        - La ventana avanza desde cada posición i hasta min(i+window, fin_texto)
    """
    c = Counter()
    if not vocab:
        return c
    
    n = len(tokens)
    # Para cada posición en el texto
    for i in range(n):
        # Si el token actual no está en el vocabulario, saltar
        if tokens[i] not in vocab: 
            continue
        
        # Definir límite de la ventana
        jmax = min(n, i + window)
        
        # Buscar co-ocurrencias dentro de la ventana
        for j in range(i+1, jmax):
            if tokens[j] not in vocab: 
                continue
            
            # Ordenar alfabéticamente para evitar duplicados (a,b) y (b,a)
            a, b = sorted((tokens[i], tokens[j]))
            
            # No contar auto-co-ocurrencias
            if a != b:
                c[(a, b)] += 1
    
    return c

def build_term_graph(
    bib_path: Path = DEFAULT_BIB,
    candidate_terms: Iterable[str] | None = None,
    min_df: int = 3,
    window: int = 30,
    min_cooc: int = 2,
) -> Dict[str, Any]:
    """
    Construye un grafo no dirigido de co-ocurrencia de términos técnicos.
    
    El grafo representa relaciones semánticas entre términos basadas en su 
    tendencia a aparecer juntos en los abstracts. Es un grafo no dirigido
    donde los nodos son términos y las aristas indican co-ocurrencia frecuente.
    
    Método de construcción:
    1. Define vocabulario: términos candidatos (Req3) o términos frecuentes (DF)
    2. Tokeniza todos los abstracts
    3. Calcula co-ocurrencias usando ventanas deslizantes
    4. Crea aristas entre términos que co-ocurren ≥ min_cooc veces
    5. Calcula grados y componentes conexas del grafo
    
    Args:
        bib_path (Path): Ruta al archivo BibTeX con los artículos
        candidate_terms (Iterable[str] | None): Lista de términos específicos a usar
                                               (ej. los 30 términos del Req3). Si es
                                               None, usa todos los términos frecuentes
        min_df (int): Frecuencia mínima de documento para incluir un término 
                     (solo aplica si candidate_terms es None)
        window (int): Tamaño de la ventana deslizante en tokens para detectar
                     co-ocurrencias (por defecto 30)
        min_cooc (int): Número mínimo de co-ocurrencias para crear una arista
                       (por defecto 2)
    
    Returns:
        Dict[str, Any]: Diccionario con la estructura completa del grafo:
            - 'nodes': Lista de nodos [{'id': término}, ...]
            - 'edges': Lista de aristas [{'u': term1, 'v': term2, 'w': frecuencia}, ...]
            - 'adj': Diccionario de adyacencia {term: {neighbor: costo}}
            - 'degree': Diccionario {término: número_de_conexiones}
            - 'components': Lista de componentes conexas [[term1, term2], [term3], ...]
            - 'params': Parámetros usados en la construcción
    
    Ejemplo de estructura retornada:
        {
            'nodes': [
                {'id': 'artificial'},
                {'id': 'intelligence'},
                {'id': 'learning'}
            ],
            'edges': [
                {'u': 'artificial', 'v': 'intelligence', 'w': 1955},
                {'u': 'artificial', 'v': 'learning', 'w': 342}
            ],
            'adj': {
                'artificial': {'intelligence': 0.000512, 'learning': 0.002924},
                'intelligence': {'artificial': 0.000512},
                'learning': {'artificial': 0.002924}
            },
            'degree': {'artificial': 2, 'intelligence': 1, 'learning': 1},
            'components': [['artificial', 'intelligence', 'learning']],
            'params': {'min_df': 3, 'window': 30, 'min_cooc': 2, 'vocab_size': 3}
        }
    
    Notas:
        - El peso 'w' en edges es la frecuencia de co-ocurrencia (mayor = más relacionado)
        - El peso en 'adj' es el costo inverso 1/w (menor = más cercano)
        - Los términos aislados (sin co-ocurrencias) aparecen como componentes de tamaño 1
        - Los términos compuestos ("machine learning") se tokenizan en palabras separadas
    """
    # === PASO 1: Cargar y tokenizar abstracts ===
    df = load_bib_dataframe(bib_path)
    # Tokeniza cada abstract en una lista de palabras individuales
    docs = [pp.tokenize(str(a)) for a in df["abstract"].tolist()]
    
    # === PASO 2: Definir vocabulario de términos ===
    if candidate_terms:
        # Opción A: Usar términos específicos proporcionados (ej. del Req3)
        # Limpia y normaliza cada término candidato
        vocab = {pp.clean(t) for t in candidate_terms if pp.clean(t)}
    else:
        # Opción B: Usar todos los términos que aparecen en suficientes documentos
        # Calcula Document Frequency (DF): número de documentos donde aparece cada término
        df_count = Counter()
        for toks in docs:
            # Cuenta cada término único por documento (no repetidos dentro del mismo doc)
            df_count.update(set(toks))
        # Filtrar términos por frecuencia mínima de documento
        vocab = {t for t, dfv in df_count.items() if dfv >= min_df}

    # === PASO 3: Calcular co-ocurrencias entre términos ===
    co = Counter()
    for toks in docs:
        # Acumula co-ocurrencias de este documento
        co.update(_window_cooccurrence(toks, vocab, window=window))

    # === PASO 4: Construir nodos y aristas del grafo ===
    # Crear un nodo por cada término en el vocabulario
    nodes = [{"id": t} for t in sorted(vocab)]
    
    edges = []
    # Diccionario de adyacencia: adj[u][v] = costo para ir de u a v
    adj: Dict[str, Dict[str, float]] = {t: {} for t in vocab}
    
    # Crear aristas solo para pares con co-ocurrencias suficientes
    for (a, b), w in co.items():
        if w >= min_cooc:
            # Agregar arista no dirigida (se representa en ambas direcciones)
            edges.append({"u": a, "v": b, "w": int(w)})
            # Costo inverso: mayor co-ocurrencia = menor costo
            # Útil para algoritmos de caminos más cortos
            adj[a][b] = float(1.0 / w)
            adj[b][a] = float(1.0 / w)

    # === PASO 5: Calcular métricas del grafo ===
    
    # Calcular grado de cada nodo (número de conexiones)
    degree = {t: 0 for t in vocab}
    for e in edges:
        a, b = e["u"], e["v"]
        degree[a] += 1
        degree[b] += 1

    # === PASO 6: Encontrar componentes conexas usando BFS ===
    # Una componente conexa es un grupo de términos conectados entre sí
    comps: List[List[str]] = []
    seen: set[str] = set()
    
    for t in vocab:
        if t in seen: 
            continue
        
        # Búsqueda en anchura (BFS) desde el término t
        q = [t]
        seen.add(t)
        comp = []
        
        while q:
            u = q.pop()
            comp.append(u)
            # Explorar todos los vecinos de u
            for v in adj[u].keys():
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        
        # Guardar la componente encontrada
        comps.append(sorted(comp))

    # === PASO 7: Retornar estructura completa del grafo ===
    return {
        "nodes": nodes,
        "edges": edges,
        "adj": adj,
        "degree": degree,
        "components": comps,
        "params": {
            "min_df": min_df, 
            "window": window, 
            "min_cooc": min_cooc, 
            "vocab_size": len(vocab)
        }
    }
