"""
Módulo de análisis de frecuencia de términos en corpus de documentos.

Funcionalidades:
- Normalización de términos para matcheo robusto
- Conteo de frecuencias por documento (soporte para n-gramas)
- Agregación de frecuencias globales del corpus
- Manejo de unigramas y bigramas

Parte del Requerimiento 3: Análisis de frecuencia de términos.
"""
from __future__ import annotations
from typing import List, Dict, Any, Iterable
from collections import Counter
from requirement_2.preprocessing import Preprocessor

_pp = Preprocessor()

def normalize_terms(terms: Iterable[str]) -> List[str]:
    """
    Normaliza lista de términos usando preprocesador para matcheo consistente.
    
    Aplica limpieza del preprocesador (minúsculas, eliminación de caracteres
    especiales, etc.) para asegurar comparaciones robustas entre términos.
    
    Args:
        terms (Iterable[str]): Términos a normalizar
    
    Returns:
        List[str]: Términos normalizados
    
    Example:
        >>> normalize_terms(["Machine Learning", "AI Models", "Deep-Learning"])
        ['machine learning', 'ai models', 'deep learning']
    
    Notas:
        - Usa Preprocessor de requirement_2 para consistencia
        - Aplica mismo preprocesamiento que tokenización
        - Facilita matcheo case-insensitive y sin caracteres especiales
        - Esencial para comparar términos semilla con texto procesado
    """
    # Normaliza términos (minúsculas y limpieza light para matcheo robusto)
    norm = []
    for t in terms:
        x = _pp.clean(t)
        norm.append(x)
    return norm

def term_frequencies_per_doc(texts: List[str], terms: List[str]) -> List[Dict[str, int]]:
    """
    Cuenta frecuencias de términos específicos en cada documento del corpus.
    
    Tokeniza cada documento y cuenta apariciones exactas de términos dados,
    soportando unigramas (1 palabra) y bigramas (2 palabras consecutivas).
    
    Args:
        texts (List[str]): Lista de documentos (abstracts/textos)
        terms (List[str]): Lista de términos a buscar (pueden ser 1-2 palabras)
    
    Returns:
        List[Dict[str, int]]: Lista de diccionarios {término: frecuencia} por documento
    
    Process:
        1. Tokeniza cada documento con preprocesador
        2. Construye bolsa de palabras con unigramas y bigramas
        3. Para cada término en la lista:
           - Divide término en palabras (tokens)
           - Busca coincidencia exacta en bolsa de palabras
           - Cuenta apariciones
        4. Retorna diccionario de frecuencias por documento
    
    Example:
        >>> docs = ["machine learning is great", "deep learning models"]
        >>> terms = ["learning", "machine learning"]
        >>> result = term_frequencies_per_doc(docs, terms)
        >>> result[0]
        {'learning': 1, 'machine learning': 1}
        >>> result[1]
        {'learning': 1, 'machine learning': 0}
    
    Notas:
        - Soporta términos de 1 o 2 palabras automáticamente
        - Usa tokenizador de requirement_2 para consistencia
        - Cuenta apariciones en forma tokenizada (no string literal)
        - Bigramas son palabras consecutivas separadas por espacio
        - Útil para tracking de términos específicos en corpus
    """
    # tokenizamos cada doc
    tokenized = [ _pp.tokenize(t) for t in texts ]
    # map de términos -> listas de tokens del término
    term_tokens = {term: term.split() for term in terms}
    per_doc = []
    for toks in tokenized:
        c = Counter()
        # índice para buscar n-gramas 1-2
        unigrams = toks
        bigrams = [" ".join(pair) for pair in zip(toks, toks[1:])]
        bag = Counter(unigrams) + Counter(bigrams)
        for term, tt in term_tokens.items():
            key = " ".join(tt)
            c[term] = bag.get(key, 0)
        per_doc.append(dict(c))
    return per_doc

def aggregate_frequencies(per_doc: List[Dict[str,int]]) -> Dict[str, int]:
    """
    Agrega frecuencias por documento en frecuencias globales del corpus.
    
    Suma frecuencias de cada término a través de todos los documentos para
    obtener conteo total en el corpus completo.
    
    Args:
        per_doc (List[Dict[str, int]]): Lista de frecuencias por documento
    
    Returns:
        Dict[str, int]: Diccionario con frecuencias totales {término: total}
    
    Example:
        >>> per_doc = [
        ...     {'learning': 2, 'ai': 1},
        ...     {'learning': 1, 'data': 3}
        ... ]
        >>> aggregate_frequencies(per_doc)
        {'learning': 3, 'ai': 1, 'data': 3}
    
    Notas:
        - Usa Counter para agregación eficiente
        - Suma todas las apariciones de cada término
        - Útil para estadísticas globales del corpus
        - Complementa análisis por documento con vista agregada
    """
    agg = Counter()
    for d in per_doc:
        agg.update(d)
    return dict(agg)
