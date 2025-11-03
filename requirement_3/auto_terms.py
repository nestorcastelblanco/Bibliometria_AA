"""
Módulo de extracción automática de términos relevantes usando TF-IDF.

Implementa extracción no supervisada de palabras clave basada en TF-IDF
para identificar términos más informativos en un corpus de documentos.

Parte del Requerimiento 3: Análisis de frecuencia de términos y generación automática.
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple
from requirement_2.preprocessing import Preprocessor

_pp = Preprocessor()

def extract_auto_terms(texts: List[str], max_terms: int = 15, min_df: int = 2, ngram_range=(1,2)) -> List[str]:
    """
    Extrae términos más informativos de un corpus usando TF-IDF sin supervisión.
    
    Implementa extracción automática de palabras clave basada en la importancia
    promedio TF-IDF de cada término en el corpus completo. Filtra términos de
    baja calidad (cortos, numéricos) y elimina duplicados.
    
    Args:
        texts (List[str]): Lista de documentos (abstracts/textos) a analizar
        max_terms (int, optional): Número máximo de términos a extraer. Default: 15
        min_df (int, optional): Frecuencia mínima de documento para considerar término. Default: 2
        ngram_range (tuple, optional): Rango de n-gramas (min, max). Default: (1,2)
    
    Returns:
        List[str]: Lista de términos ordenados por importancia TF-IDF
    
    Process:
        1. Vectoriza textos usando TF-IDF con tokenizador del preprocesador
        2. Calcula importancia global = media TF-IDF de cada término
        3. Filtra términos de calidad (longitud >= 3, no numéricos)
        4. Ordena por importancia descendente
        5. Elimina duplicados manteniendo orden
        6. Retorna top max_terms términos
    
    Filtros de calidad:
        - Longitud mínima: 3 caracteres
        - Rechaza términos con dígitos numéricos
        - Elimina duplicados preservando primer ocurrencia
    
    Example:
        >>> docs = ["machine learning models", "deep learning neural networks", "ai models"]
        >>> extract_auto_terms(docs, max_terms=3)
        ['learning', 'models', 'neural networks']
    
    Notas:
        - Usa tokenizador de requirement_2.preprocessing para consistencia
        - min_df ayuda a filtrar términos muy raros (ruido)
        - ngram_range=(1,2) captura unigramas y bigramas
        - No requiere etiquetas ni términos semilla (no supervisado)
        - Útil para descubrimiento exploratorio de temas
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(
        tokenizer=_pp.tokenize, preprocessor=None, lowercase=False, stop_words=None,
        token_pattern=None, ngram_range=ngram_range, min_df=min_df
    )
    X = vec.fit_transform(texts)
    vocab = {v: k for k, v in vec.vocabulary_.items()}
    # importancia global = media TF-IDF de cada término en el corpus
    import numpy as np
    mean_tfidf = X.mean(axis=0).A1  # array
    items = [(vocab[i], float(w)) for i, w in enumerate(mean_tfidf)]
    # filtros de calidad
    def good(term: str) -> bool:
        # evita tokens demasiado cortos o numéricos
        if len(term) < 3: return False
        if any(ch.isdigit() for ch in term): return False
        return True
    ranked = [t for t in sorted(items, key=lambda x: -x[1]) if good(t[0])]
    top = []
    seen = set()
    for term, _ in ranked:
        if term in seen: continue
        seen.add(term)
        top.append(term)
        if len(top) >= max_terms: break
    return top
